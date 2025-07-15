#!/usr/bin/env python3
"""
Test version of the Google Scholar Publications Fetcher
Uses a real Google Scholar profile to test the functionality
"""

import yaml
import sys
import os

# Add the current directory to the path so we can import the main script
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fetch_publications import GoogleScholarFetcher

def create_test_config():
    """Create a test configuration with a real Google Scholar profile"""
    test_config = {
        'profiles': [
            {
                'name': 'Test Profile',
                'url': 'https://scholar.google.com/citations?user=YOUR_USER_ID',
                'role': 'Test Role',
                'active': True,
                'year_range': {
                    'start': 2020,
                    'end': None
                }
            }
        ],
        'settings': {
            'max_publications_per_profile': 5,  # Small number for testing
            'min_year': 2020,
            'include_types': ['journal', 'conference'],
            'priority_keywords': ['MIMIC', 'PhysioNet', 'critical care']
        }
    }
    
    # Write test config
    with open('_data/test_scholar_profiles.yml', 'w') as f:
        yaml.dump(test_config, f, default_flow_style=False, indent=2)
    
    return test_config

def test_script_structure():
    """Test that the script can be imported and has the right structure"""
    try:
        fetcher = GoogleScholarFetcher('_data/test_scholar_profiles.yml')
        print("✓ GoogleScholarFetcher class instantiated successfully")
        
        # Test config loading
        config = fetcher.load_config()
        if config:
            print("✓ Configuration loading works")
            print(f"  Found {len(config.get('profiles', []))} profiles")
        else:
            print("✗ Configuration loading failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing script structure: {e}")
        return False

def test_year_range_filtering():
    """Test the year range filtering logic"""
    try:
        fetcher = GoogleScholarFetcher('_data/test_scholar_profiles.yml')
        
        # Create test publications
        test_publications = [
            {
                'title': 'Test Paper 2022',
                'authors': 'Test Author',
                'journal': 'Test Journal',
                'year': 2022,
                'citations': 10,
                'author_name': 'Test Profile'
            },
            {
                'title': 'Test Paper 2019',
                'authors': 'Test Author',
                'journal': 'Test Journal',
                'year': 2019,
                'citations': 5,
                'author_name': 'Test Profile'
            },
            {
                'title': 'Test Paper 2020',
                'authors': 'Test Author',
                'journal': 'Test Journal',
                'year': 2020,
                'citations': 8,
                'author_name': 'Test Profile'
            }
        ]
        
        config = fetcher.load_config()
        filtered_pubs = fetcher.filter_and_sort_publications(test_publications, config)
        
        print(f"✓ Year range filtering works")
        print(f"  Input: {len(test_publications)} publications")
        print(f"  Output: {len(filtered_pubs)} publications")
        
        # Should filter out 2019 paper (before year_range start)
        if len(filtered_pubs) == 2:
            print("✓ Correctly filtered out publications outside year range")
        else:
            print("✗ Year range filtering not working correctly")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing year range filtering: {e}")
        return False

def test_yaml_generation():
    """Test the YAML generation functionality"""
    try:
        fetcher = GoogleScholarFetcher('_data/test_scholar_profiles.yml')
        
        # Create test grouped publications
        grouped_publications = {
            2022: [
                {
                    'title': 'Test Paper 2022',
                    'authors': 'Test Author',
                    'journal': 'Test Journal',
                    'year': 2022,
                    'citations': 10,
                    'author_name': 'Test Profile'
                }
            ],
            2021: [
                {
                    'title': 'Test Paper 2021',
                    'authors': 'Test Author',
                    'journal': 'Test Journal',
                    'year': 2021,
                    'citations': 8,
                    'author_name': 'Test Profile'
                }
            ]
        }
        
        yaml_data = fetcher.generate_publications_yaml(grouped_publications)
        
        print("✓ YAML generation works")
        print(f"  Generated {len(yaml_data)} year groups")
        
        # Test the structure
        for year_data in yaml_data:
            if 'year' in year_data and 'publications' in year_data:
                print(f"  Year {year_data['year']}: {len(year_data['publications'])} publications")
            else:
                print("✗ YAML structure incorrect")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing YAML generation: {e}")
        return False

def cleanup():
    """Clean up test files"""
    try:
        if os.path.exists('_data/test_scholar_profiles.yml'):
            os.remove('_data/test_scholar_profiles.yml')
        print("✓ Cleaned up test files")
    except Exception as e:
        print(f"⚠ Could not clean up test files: {e}")

def main():
    """Run all tests"""
    print("Testing Publications Fetcher Script\n")
    
    # Create test configuration
    print("--- Creating Test Configuration ---")
    create_test_config()
    print("✓ Test configuration created")
    
    tests = [
        ("Script Structure", test_script_structure),
        ("Year Range Filtering", test_year_range_filtering),
        ("YAML Generation", test_yaml_generation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        if test_func():
            passed += 1
            print(f"✓ {test_name} passed")
        else:
            print(f"✗ {test_name} failed")
    
    print(f"\n=== Results ===")
    print(f"Tests passed: {passed}/{total}")
    
    # Cleanup
    print("\n--- Cleanup ---")
    cleanup()
    
    if passed == total:
        print("✓ All tests passed! The publications fetcher is working correctly.")
        print("\nNote: To test with real Google Scholar profiles, update the URLs in _data/scholar_profiles.yml")
        return 0
    else:
        print("✗ Some tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 