#!/usr/bin/env python3
"""
Test all API endpoints to check which ones need trailing slash.
"""

import requests
import json

BASE_URL = 'https://v2asbest-tool-production.up.railway.app'

def test_endpoint_consistency():
    """Test all API endpoints for trailing slash consistency."""
    
    print("🔍 TESTING API ENDPOINT CONSISTENCY")
    print("=" * 60)
    
    # Login
    response = requests.post(f"{BASE_URL}/auth/jwt/login", data={
        "username": "admin@bedrijfy.nl",
        "password": "Admin123!"
    })
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code}")
        return
    
    token = response.json().get('access_token')
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test endpoints found in UI
    endpoints_to_test = [
        # Health check
        ("/healthz", "GET", False),
        ("/healthz/", "GET", False),
        
        # Reports
        ("/reports", "GET", True),
        ("/reports/", "GET", True),
        
        # Users
        ("/users", "GET", True),
        ("/users/", "GET", True),
        ("/users/me", "GET", True),
        ("/users/me/", "GET", True),
        
        # Tenants
        ("/tenants", "GET", True),
        ("/tenants/", "GET", True),
    ]
    
    print("Testing endpoints...")
    print("-" * 60)
    
    for endpoint, method, needs_auth in endpoints_to_test:
        test_headers = headers if needs_auth else {}
        
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}", headers=test_headers)
            else:
                response = requests.post(f"{BASE_URL}{endpoint}", headers=test_headers)
            
            status = response.status_code
            if status == 200:
                print(f"✅ {endpoint:<15} - {status} OK")
            elif status == 401:
                print(f"🔒 {endpoint:<15} - {status} Unauthorized (expected for protected)")
            elif status == 404:
                print(f"❌ {endpoint:<15} - {status} Not Found")
            else:
                print(f"⚠️  {endpoint:<15} - {status} {response.text[:50]}")
                
        except Exception as e:
            print(f"💥 {endpoint:<15} - Error: {str(e)[:50]}")
    
    print("\n" + "=" * 60)
    print("🎯 RECOMMENDATIONS:")
    print("=" * 60)
    
    # Test specific problematic endpoints
    print("\n🔍 Testing specific UI endpoints...")
    
    # Test /users endpoint
    response = requests.get(f"{BASE_URL}/users", headers=headers)
    users_without_slash = response.status_code
    
    response = requests.get(f"{BASE_URL}/users/", headers=headers)
    users_with_slash = response.status_code
    
    print(f"/users:  {users_without_slash}")
    print(f"/users/: {users_with_slash}")
    
    if users_without_slash != users_with_slash:
        print("⚠️  /users endpoint inconsistency detected!")
    
    # Test /tenants endpoint
    response = requests.get(f"{BASE_URL}/tenants", headers=headers)
    tenants_without_slash = response.status_code
    
    response = requests.get(f"{BASE_URL}/tenants/", headers=headers)
    tenants_with_slash = response.status_code
    
    print(f"/tenants:  {tenants_without_slash}")
    print(f"/tenants/: {tenants_with_slash}")
    
    if tenants_without_slash != tenants_with_slash:
        print("⚠️  /tenants endpoint inconsistency detected!")

if __name__ == "__main__":
    test_endpoint_consistency()
