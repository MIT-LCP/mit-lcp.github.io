# Automated Publications System

This system automatically fetches publications from Google Scholar profiles and updates the lab website's publications page.

## Setup

### 1. Configure Google Scholar Profiles

Edit `_data/scholar_profiles.yml` and add the Google Scholar profile URLs for lab members:

```yaml
profiles:
  - name: "Leo Anthony Celi"
    url: "https://scholar.google.com/citations?user=YOUR_USER_ID"
    role: "Principal Investigator"
    active: true
    year_range:
      start: 2010  # Year they joined the lab
      end: null    # null means current year (still in lab)
  
  - name: "Former Lab Member"
    url: "https://scholar.google.com/citations?user=YOUR_USER_ID"
    role: "Postdoc"
    active: true
    year_range:
      start: 2015  # Year they joined the lab
      end: 2020    # Year they left the lab
```

To find your Google Scholar user ID:
1. Go to your Google Scholar profile
2. Look at the URL: `https://scholar.google.com/citations?user=USER_ID_HERE`
3. Copy the `USER_ID_HERE` part

### 2. Configuration Options

In `_data/scholar_profiles.yml`, you can configure:

- **max_publications_per_profile**: Maximum publications to fetch per person
- **min_year**: Global minimum year (fallback if no year_range specified)
- **include_types**: Types of publications to include
- **priority_keywords**: Keywords that give publications higher priority

#### Year Range Filtering

Each profile can have a `year_range` to only include publications from when they were in the lab:

- **start**: Year they joined the lab
- **end**: Year they left the lab (use `null` for current members)

This ensures only relevant publications are included, even if researchers have publications from other institutions.

### 3. GitHub Actions Setup

The system uses GitHub Actions to automatically update publications weekly. The workflow:

- Runs every Sunday at 2 AM UTC
- Can be triggered manually via GitHub Actions tab
- Only commits changes if new publications are found
- Creates an issue if the update fails

## Manual Usage

To run the script manually:

```bash
cd scripts
pip install -r requirements.txt
python fetch_publications.py
```

## How It Works

1. **Fetch**: The script fetches publications from each Google Scholar profile
2. **Parse**: Extracts title, authors, journal, year, citations, and links
3. **Filter**: Removes old publications and prioritizes relevant ones
4. **Sort**: Orders by relevance, year, and citation count
5. **Generate**: Creates the `_data/publications.yml` file
6. **Update**: The website automatically displays the new publications

## Troubleshooting

### Rate Limiting
Google Scholar may block requests if too many are made too quickly. The script includes delays, but you may need to:
- Reduce the number of profiles
- Increase delays in the script
- Use a VPN or different IP

### Missing Publications
If publications are missing:
- Check that the Google Scholar URL is correct
- Verify the profile is public
- Check that publications are recent enough (see min_year setting)
- Verify the year_range settings are correct for each researcher
- Check the logs for "Filtered out X publications due to year range restrictions"

### Script Errors
If the script fails:
- Check the GitHub Actions logs
- Verify all dependencies are installed
- Ensure the configuration file is valid YAML

## Customization

### Adding New Profile Fields
To add new fields to profiles (e.g., department, keywords):

1. Update `_data/scholar_profiles.yml`
2. Modify `fetch_publications.py` to use the new fields
3. Update the publications template if needed

### Changing Update Frequency
Edit `.github/workflows/update-publications.yml`:

```yaml
schedule:
  # Run daily at 2 AM UTC
  - cron: '0 2 * * *'
  
  # Run monthly on the 1st
  - cron: '0 2 1 * *'
```

### Filtering Publications
To change how publications are filtered:

1. Modify the `filter_and_sort_publications` method in `fetch_publications.py`
2. Add new keywords to `priority_keywords` in the config
3. Adjust the `min_year` setting

## Security Notes

- The script uses a realistic User-Agent to avoid blocking
- It includes random delays between requests
- It respects robots.txt and rate limiting
- Consider using a dedicated service account for production use

## Dependencies

- `requests`: HTTP requests
- `beautifulsoup4`: HTML parsing
- `pyyaml`: YAML file handling
- `lxml`: XML/HTML parser (faster than default) 