#!/usr/bin/env python3
"""
Test script om te controleren of de trailing slash fix in de UI werkt
"""

import requests
import json

def test_prompts_endpoint():
    """Test de prompts endpoint met en zonder trailing slash"""
    base_url = "https://v2asbest-tool-production.up.railway.app"
    
    print("Testing prompts endpoint...")
    
    # Test zonder trailing slash
    url_without_slash = f"{base_url}/admin/prompts"
    print(f"\n1. Testing WITHOUT trailing slash: {url_without_slash}")
    
    try:
        response = requests.get(url_without_slash, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Final URL: {response.url}")
        print(f"   Redirects: {len(response.history)}")
        
        if response.history:
            print("   Redirect chain:")
            for i, redirect in enumerate(response.history):
                print(f"     {i+1}. {redirect.status_code} {redirect.url}")
        
        if response.url.startswith('https://'):
            print("   ✅ Final URL is HTTPS")
        else:
            print("   ❌ Final URL is NOT HTTPS!")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test met trailing slash
    url_with_slash = f"{base_url}/admin/prompts/"
    print(f"\n2. Testing WITH trailing slash: {url_with_slash}")
    
    try:
        response = requests.get(url_with_slash, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Final URL: {response.url}")
        print(f"   Redirects: {len(response.history)}")
        
        if response.history:
            print("   Redirect chain:")
            for i, redirect in enumerate(response.history):
                print(f"     {i+1}. {redirect.status_code} {redirect.url}")
        
        if response.url.startswith('https://'):
            print("   ✅ Final URL is HTTPS")
        else:
            print("   ❌ Final URL is NOT HTTPS!")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "="*60)
    print("CONCLUSIE:")
    print("Als de trailing slash fix werkt, zou de UI nu moeten werken")
    print("zonder Mixed Content errors.")
    print("="*60)

if __name__ == "__main__":
    test_prompts_endpoint()
