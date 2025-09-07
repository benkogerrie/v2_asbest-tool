#!/usr/bin/env python3
"""
Simple test to isolate the reports endpoint issue.
"""

import requests
import json

BASE_URL = 'https://v2asbest-tool-production.up.railway.app'

def test_simple_reports():
    """Test reports endpoint with minimal parameters."""
    
    print("🔍 Testing reports endpoint isolation...")
    
    # Get token
    response = requests.post(f"{BASE_URL}/auth/jwt/login", data={
        "username": "admin@bedrijfy.nl",
        "password": "Admin123!"
    })
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code}")
        return
    
    token = response.json().get('access_token')
    headers = {"Authorization": f"Bearer {token}"}
    
    print("✅ Login successful")
    
    # Test different report endpoints
    endpoints_to_test = [
        "/reports",
        "/reports?page=1",
        "/reports?page=1&page_size=10",
        "/reports?page=1&page_size=10&sort=uploaded_at_desc"
    ]
    
    for endpoint in endpoints_to_test:
        print(f"\n🔍 Testing {endpoint}...")
        response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ Success!")
            data = response.json()
            print(f"   - Total: {data.get('total', 'N/A')}")
            print(f"   - Items: {len(data.get('items', []))}")
        else:
            print(f"   ❌ Failed: {response.text}")
            
            # Try to get more details
            if response.status_code == 401:
                print(f"   - 401 Unauthorized - authentication issue")
            elif response.status_code == 500:
                print(f"   - 500 Internal Server Error - server issue")
            elif response.status_code == 422:
                print(f"   - 422 Validation Error - parameter issue")
    
    # Test with system owner
    print(f"\n🔍 Testing with system owner...")
    response = requests.post(f"{BASE_URL}/auth/jwt/login", data={
        "username": "system@asbest-tool.nl",
        "password": "SystemOwner123!"
    })
    
    if response.status_code == 200:
        token = response.json().get('access_token')
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(f"{BASE_URL}/reports", headers=headers)
        print(f"   System owner /reports: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ System owner can see reports: {data.get('total', 0)} total")
        else:
            print(f"   ❌ System owner also fails: {response.text}")
    else:
        print(f"   ❌ System owner login failed: {response.status_code}")

if __name__ == "__main__":
    test_simple_reports()
