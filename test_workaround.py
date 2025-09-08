#!/usr/bin/env python3
"""
Test workaround voor Railway redirect probleem
"""

import requests

def test_direct_https():
    """Test direct HTTPS zonder redirects"""
    print("🔍 Testing direct HTTPS without redirects...")
    
    # Test met verschillende URL formats
    urls = [
        "https://v2asbest-tool-production.up.railway.app/admin/prompts",
        "https://v2asbest-tool-production.up.railway.app/admin/prompts/",
        "https://v2asbest-tool-production.up.railway.app/admin/prompts?",
    ]
    
    for url in urls:
        try:
            print(f"\nTesting: {url}")
            response = requests.get(url, allow_redirects=False, timeout=10)
            print(f"  Status: {response.status_code}")
            print(f"  Location header: {response.headers.get('Location', 'None')}")
            if response.status_code == 200:
                print(f"  Content: {response.text[:100]}")
        except Exception as e:
            print(f"  Error: {e}")

if __name__ == "__main__":
    test_direct_https()
