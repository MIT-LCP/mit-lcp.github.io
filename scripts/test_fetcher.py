#!/usr/bin/env python3
"""
Test script for the Google Scholar Publications Fetcher
"""

import yaml
import sys
import os

def test_config_loading():
    """Test that the configuration file can be loaded"""
    try:
        with open('_data/scholar_profiles.yml', 'r') as f:
            config = yaml.safe_load(f)
        
        print("✓ Configuration file loaded successfully")
        
        # Check required fields
        if 'profiles' not in config:
            print("✗ Missing 'profiles' section in config")
            return False
        
        if 'settings' not in config:
            print("✗ Missing 'settings' section in config")
            return False
        
        # Check profile configurations
        profiles = config.get('profiles', [])
        print(f"✓ Found {len(profiles)} profiles")
        
        for i, profile in enumerate(profiles):
            print(f"  Profile {i+1}: {profile.get('name', 'Unknown')}")
            
            # Check for year_range
            if 'year_range' in profile:
                year_range = profile['year_range']
                start = year_range.get('start', 'Not set')
                end = year_range.get('end', 'Not set')
                print(f"    Year range: {start} - {end}")
            else:
                print(f"    Year range: Not specified (will use global min_year)")
        
        print("✓ Configuration structure is valid")
        return True
        
    except FileNotFoundError:
        print("✗ Configuration file not found: _data/scholar_profiles.yml")
        return False
    except yaml.YAMLError as e:
        print(f"✗ Error parsing configuration file: {e}")
        return False

def test_dependencies():
    """Test that required dependencies are available"""
    try:
        import requests
        print("✓ requests module available")
    except ImportError:
        print("✗ requests module not available")
        return False
    
    try:
        import bs4
        print("✓ beautifulsoup4 module available")
    except ImportError:
        print("✗ beautifulsoup4 module not available")
        return False
    
    try:
        import yaml
        print("✓ pyyaml module available")
    except ImportError:
        print("✗ pyyaml module not available")
        return False
    
    return True

def test_output_directory():
    """Test that output directory exists"""
    if os.path.exists('_data'):
        print("✓ _data directory exists")
        return True
    else:
        print("✗ _data directory not found")
        return False

def main():
    """Run all tests"""
    print("Testing Google Scholar Publications Fetcher Setup\n")
    
    tests = [
        test_dependencies,
        test_config_loading,
        test_output_directory
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All tests passed! The fetcher should work correctly.")
        return 0
    else:
        print("✗ Some tests failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 