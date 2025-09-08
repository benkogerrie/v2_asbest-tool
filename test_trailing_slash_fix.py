#!/usr/bin/env python3
"""
Test script om te controleren of trailing slash fix werkt
en of andere endpoints zoals /docs hetzelfde probleem hebben
"""

import requests
import sys

def test_endpoint(url, description):
    """Test een endpoint en rapporteer de resultaten"""
    print(f"\n=== {description} ===")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, allow_redirects=True, timeout=10)
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
            
        return response.status_code == 200 and response.url.startswith('https://')
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    base_url = "https://v2asbest-tool-production.up.railway.app"
    
    print("Testing Railway endpoints for trailing slash redirect issues...")
    
    # Test verschillende endpoints
    endpoints_to_test = [
        ("/docs", "FastAPI Docs (zonder trailing slash)"),
        ("/docs/", "FastAPI Docs (met trailing slash)"),
        ("/admin/prompts", "Admin Prompts (zonder trailing slash)"),
        ("/admin/prompts/", "Admin Prompts (met trailing slash)"),
        ("/healthz", "Health Check (zonder trailing slash)"),
        ("/healthz/", "Health Check (met trailing slash)"),
        ("/reports/", "Reports (met trailing slash)"),
        ("/tenants/", "Tenants (met trailing slash)"),
    ]
    
    results = []
    
    for endpoint, description in endpoints_to_test:
        url = base_url + endpoint
        success = test_endpoint(url, description)
        results.append((endpoint, description, success))
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    for endpoint, description, success in results:
        status = "✅ OK" if success else "❌ PROBLEEM"
        print(f"{status} {endpoint} - {description}")
    
    # Check if /docs has the same issue
    docs_without_slash = any(not success for endpoint, _, success in results if endpoint == "/docs")
    docs_with_slash = any(success for endpoint, _, success in results if endpoint == "/docs/")
    
    print(f"\n/docs zonder slash: {'❌ Probleem' if docs_without_slash else '✅ OK'}")
    print(f"/docs met slash: {'✅ OK' if docs_with_slash else '❌ Probleem'}")
    
    if docs_without_slash and docs_with_slash:
        print("\n🔍 CONCLUSIE: /docs heeft hetzelfde probleem als /admin/prompts!")
        print("   - Zonder trailing slash: redirect naar HTTP")
        print("   - Met trailing slash: werkt direct met HTTPS")
    else:
        print("\n🔍 CONCLUSIE: /docs heeft GEEN trailing slash probleem")

if __name__ == "__main__":
    main()
