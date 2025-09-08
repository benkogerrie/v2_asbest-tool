#!/usr/bin/env python3
"""
Test script om te controleren of alle endpoints correct werken met trailing slashes
"""

import requests
import json

def test_endpoint(url, description, expected_status=200):
    """Test een endpoint en rapporteer de resultaten"""
    print(f"\n=== {description} ===")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Final URL: {response.url}")
        print(f"Redirects: {len(response.history)}")
        
        if response.history:
            print("Redirect chain:")
            for i, redirect in enumerate(response.history):
                print(f"  {i+1}. {redirect.status_code} {redirect.url}")
        
        # Check if final URL is HTTPS
        if response.url.startswith('https://'):
            print("✅ Final URL is HTTPS")
        else:
            print("❌ Final URL is NOT HTTPS!")
            
        # Check status
        if response.status_code == expected_status:
            print(f"✅ Status {response.status_code} is correct")
        else:
            print(f"❌ Status {response.status_code} is not expected {expected_status}")
            
        return response.status_code == expected_status and response.url.startswith('https://')
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    base_url = "https://v2asbest-tool-production.up.railway.app"
    
    print("Testing all UI endpoints for trailing slash compatibility...")
    
    # Test endpoints die de UI gebruikt
    endpoints_to_test = [
        ("/healthz/", "Health Check", 200),
        ("/admin/prompts/", "Admin Prompts List", 200),
        ("/tenants/", "Tenants List", 401),  # 401 is expected zonder auth
        ("/users/", "Users List", 401),      # 401 is expected zonder auth
        ("/reports/", "Reports List", 401),  # 401 is expected zonder auth
    ]
    
    results = []
    
    for endpoint, description, expected_status in endpoints_to_test:
        url = base_url + endpoint
        success = test_endpoint(url, description, expected_status)
        results.append((endpoint, description, success))
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    all_success = True
    for endpoint, description, success in results:
        status = "✅ OK" if success else "❌ PROBLEEM"
        print(f"{status} {endpoint} - {description}")
        if not success:
            all_success = False
    
    if all_success:
        print("\n🎉 ALLE ENDPOINTS WERKEN CORRECT!")
        print("De trailing slash fix zou het Mixed Content probleem moeten oplossen.")
    else:
        print("\n⚠️  Sommige endpoints hebben nog problemen.")
    
    print("\n" + "="*60)
    print("VOLGENDE STAP:")
    print("Test de UI in de browser om te zien of het Mixed Content")
    print("probleem is opgelost.")
    print("="*60)

if __name__ == "__main__":
    main()
