#!/usr/bin/env python3
"""
Google Scholar Publications Fetcher
Fetches publications from Google Scholar profiles and generates publications.yml
"""

import yaml
import requests
from bs4 import BeautifulSoup, Tag
import re
import time
import random
from datetime import datetime
from urllib.parse import urljoin, urlparse
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GoogleScholarFetcher:
    def __init__(self, config_file='_data/scholar_profiles.yml'):
        self.config_file = config_file
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def load_config(self):
        """Load the scholar profiles configuration"""
        try:
            with open(self.config_file, 'r') as f:
                config = yaml.safe_load(f)
            return config
        except FileNotFoundError:
            logger.error(f"Configuration file {self.config_file} not found")
            return None
        except yaml.YAMLError as e:
            logger.error(f"Error parsing configuration file: {e}")
            return None
    
    def extract_user_id(self, url):
        """Extract user ID from Google Scholar URL"""
        match = re.search(r'user=([^&]+)', url)
        return match.group(1) if match else None
    
    def fetch_profile_publications(self, profile):
        """Fetch publications from a Google Scholar profile"""
        if not profile.get('active', True):
            logger.info(f"Skipping inactive profile: {profile['name']}")
            return []
        
        user_id = self.extract_user_id(profile['url'])
        if not user_id:
            logger.error(f"Could not extract user ID from URL: {profile['url']}")
            return []
        
        publications = []
        page = 0
        
        while page < 5:  # Limit to 5 pages to avoid rate limiting
            try:
                # Construct the publications URL
                url = f"https://scholar.google.com/citations?user={user_id}&hl=en&oi=ao&cstart={page * 20}"
                
                logger.info(f"Fetching publications for {profile['name']} (page {page + 1})")
                
                response = self.session.get(url)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find publication entries
                pub_entries = soup.find_all('tr', class_='gsc_a_tr')
                
                if not pub_entries:
                    logger.info(f"No more publications found for {profile['name']}")
                    break
                
                for entry in pub_entries:
                    pub = self.parse_publication_entry(entry, profile['name'])
                    if pub:
                        publications.append(pub)
                
                # Check if there are more pages
                next_button = soup.find('button', {'id': 'gsc_bpf_more'})
                if not next_button:
                    break
                try:
                    if 'disabled' in next_button.get('class', []):
                        break
                except AttributeError:
                    break
                
                page += 1
                time.sleep(random.uniform(2, 5))  # Random delay to avoid rate limiting
                
            except requests.RequestException as e:
                logger.error(f"Error fetching publications for {profile['name']}: {e}")
                break
            except Exception as e:
                logger.error(f"Unexpected error for {profile['name']}: {e}")
                break
        
        return publications
    
    def parse_publication_entry(self, entry, author_name):
        """Parse a single publication entry from Google Scholar"""
        try:
            # Extract title and link
            title_elem = entry.find('a', class_='gsc_a_at')
            if not title_elem:
                return None
            
            title = title_elem.get_text(strip=True)
            link = title_elem.get('href')
            if link:
                link = urljoin('https://scholar.google.com', link)
            
            # Extract authors
            authors_elem = entry.find('div', class_='gs_gray')
            authors = authors_elem.get_text(strip=True) if authors_elem else ""
            
            # Extract journal/conference
            journal_elem = entry.find('div', class_='gs_gray').find_next_sibling('div', class_='gs_gray')
            journal = journal_elem.get_text(strip=True) if journal_elem else ""
            
            # Extract year
            year_elem = entry.find('span', class_='gsc_a_h')
            year = year_elem.get_text(strip=True) if year_elem else ""
            
            # Extract citations
            citations_elem = entry.find('a', class_='gsc_a_ac')
            citations = citations_elem.get_text(strip=True) if citations_elem else "0"
            
            # Try to extract more details from the publication page
            details = self.fetch_publication_details(link) if link else {}
            
            publication = {
                'title': title,
                'authors': authors,
                'journal': journal,
                'year': int(year) if year.isdigit() else None,
                'citations': int(citations) if citations.isdigit() else 0,
                'url': link,
                'author_name': author_name,
                **details
            }
            
            return publication
            
        except Exception as e:
            logger.error(f"Error parsing publication entry: {e}")
            return None
    
    def fetch_publication_details(self, url):
        """Fetch additional details from the publication page"""
        details = {}
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract DOI
            doi_elem = soup.find('div', string=re.compile(r'DOI', re.I))
            if doi_elem:
                doi_text = doi_elem.get_text()
                doi_match = re.search(r'10\.\d+/[^\s]+', doi_text)
                if doi_match:
                    details['doi'] = doi_match.group(0)
            
            # Extract volume and pages
            journal_info = soup.find('div', class_='gs_scl')
            if journal_info:
                journal_text = journal_info.get_text()
                
                # Extract volume
                vol_match = re.search(r'(\d+)\s*\((\d+)\)', journal_text)
                if vol_match:
                    details['volume'] = f"{vol_match.group(1)}({vol_match.group(2)})"
                
                # Extract pages
                pages_match = re.search(r'(\d+)-(\d+)', journal_text)
                if pages_match:
                    details['pages'] = f"{pages_match.group(1)}-{pages_match.group(2)}"
            
            time.sleep(random.uniform(1, 3))  # Small delay
            
        except Exception as e:
            logger.debug(f"Error fetching publication details: {e}")
        
        return details
    
    def filter_and_sort_publications(self, publications, config):
        """Filter and sort publications based on configuration"""
        settings = config.get('settings', {})
        min_year = settings.get('min_year', 2010)
        priority_keywords = settings.get('priority_keywords', [])
        current_year = datetime.now().year
        
        # Filter by year range for each author
        filtered_pubs = []
        filtered_out_count = 0
        
        for pub in publications:
            pub_year = pub.get('year', 0)
            author_name = pub.get('author_name', '')
            
            # Find the author's profile to get their year range
            author_profile = None
            for profile in config.get('profiles', []):
                if profile['name'] == author_name:
                    author_profile = profile
                    break
            
            if author_profile and 'year_range' in author_profile:
                year_range = author_profile['year_range']
                start_year = year_range.get('start', min_year)
                end_year = year_range.get('end', current_year)
                
                # Check if publication is within the author's year range
                # Handle None end_year (current year)
                if end_year is None:
                    end_year = current_year
                
                # Handle None pub_year (skip publications without year)
                if pub_year is None:
                    filtered_out_count += 1
                    logger.debug(f"Filtered out {pub.get('title', 'Unknown')} (no year) by {author_name} - missing year")
                elif start_year <= pub_year <= end_year:
                    filtered_pubs.append(pub)
                else:
                    filtered_out_count += 1
                    logger.debug(f"Filtered out {pub.get('title', 'Unknown')} ({pub_year}) by {author_name} - outside year range {start_year}-{end_year}")
            else:
                # Fallback to global min_year if no year range specified
                if pub_year is None:
                    filtered_out_count += 1
                    logger.debug(f"Filtered out {pub.get('title', 'Unknown')} (no year) by {author_name} - missing year")
                elif pub_year >= min_year:
                    filtered_pubs.append(pub)
                else:
                    filtered_out_count += 1
        
        if filtered_out_count > 0:
            logger.info(f"Filtered out {filtered_out_count} publications due to year range restrictions")
        
        # Score publications based on priority keywords
        for pub in filtered_pubs:
            score = 0
            title_lower = pub.get('title', '').lower()
            journal_lower = pub.get('journal', '').lower()
            
            for keyword in priority_keywords:
                if keyword.lower() in title_lower or keyword.lower() in journal_lower:
                    score += 1
            
            pub['priority_score'] = score
        
        # Sort by priority score (descending), then by year (descending), then by citations (descending)
        filtered_pubs.sort(key=lambda x: (-x.get('priority_score', 0), -x.get('year', 0), -x.get('citations', 0)))
        
        return filtered_pubs
    
    def group_by_year(self, publications):
        """Group publications by year"""
        grouped = {}
        
        for pub in publications:
            year = pub.get('year')
            if year:
                if year not in grouped:
                    grouped[year] = []
                grouped[year].append(pub)
        
        return grouped
    
    def generate_publications_yaml(self, grouped_publications):
        """Generate the publications YAML file"""
        yaml_data = []
        
        # Sort years in descending order
        for year in sorted(grouped_publications.keys(), reverse=True):
            year_data = {
                'year': year,
                'publications': []
            }
            
            for pub in grouped_publications[year]:
                # Convert to the format expected by the website
                publication_entry = {
                    'title': pub['title'],
                    'authors': pub['authors'],
                    'journal': pub['journal'],
                    'year': year,
                    'type': 'journal'  # Default type
                }
                
                # Add optional fields if available
                if pub.get('volume'):
                    publication_entry['volume'] = pub['volume']
                if pub.get('pages'):
                    publication_entry['pages'] = pub['pages']
                if pub.get('doi'):
                    publication_entry['doi'] = pub['doi']
                if pub.get('url'):
                    publication_entry['url'] = pub['url']
                
                year_data['publications'].append(publication_entry)
            
            yaml_data.append(year_data)
        
        return yaml_data
    
    def run(self):
        """Main execution function"""
        logger.info("Starting Google Scholar publications fetch")
        
        # Load configuration
        config = self.load_config()
        if not config:
            return False
        
        all_publications = []
        
        # Fetch publications from each profile
        for profile in config.get('profiles', []):
            logger.info(f"Processing profile: {profile['name']}")
            publications = self.fetch_profile_publications(profile)
            all_publications.extend(publications)
            
            # Add delay between profiles
            time.sleep(random.uniform(5, 10))
        
        # Filter and sort publications
        filtered_publications = self.filter_and_sort_publications(all_publications, config)
        
        # Group by year
        grouped_publications = self.group_by_year(filtered_publications)
        
        # Generate YAML data
        yaml_data = self.generate_publications_yaml(grouped_publications)
        
        # Write to file
        output_file = '_data/publications.yml'
        try:
            with open(output_file, 'w') as f:
                yaml.dump(yaml_data, f, default_flow_style=False, sort_keys=False, indent=2)
            
            logger.info(f"Successfully wrote {len(filtered_publications)} publications to {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error writing publications file: {e}")
            return False

if __name__ == "__main__":
    fetcher = GoogleScholarFetcher()
    success = fetcher.run()
    exit(0 if success else 1) 