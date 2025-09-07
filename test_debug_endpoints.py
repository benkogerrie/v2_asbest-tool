#!/usr/bin/env python3
"""
Test debug endpoints to isolate authentication issue.
"""

import requests
import json

BASE_URL = 'https://v2asbest-tool-production.up.railway.app'

def test_debug_endpoints():
    """Test debug endpoints to isolate where authentication fails."""
    
    print("🔍 Testing debug endpoints to isolate authentication issue...")
    
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
    
    # Test debug endpoints
    debug_endpoints = [
        "/debug/test-auth-1",
        "/debug/test-auth-2", 
        "/debug/test-auth-3"
    ]
    
    for endpoint in debug_endpoints:
        print(f"\n🔍 Testing {endpoint}...")
        response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ Success!")
            result = response.json()
            print(f"   - Method: {result.get('method', 'N/A')}")
            print(f"   - User ID: {result.get('user_id', 'N/A')}")
            print(f"   - User Email: {result.get('user_email', 'N/A')}")
            print(f"   - User Role: {result.get('user_role', 'N/A')}")
            if 'session_active' in result:
                print(f"   - Session Active: {result.get('session_active', 'N/A')}")
            if 'report_count' in result:
                print(f"   - Report Count: {result.get('report_count', 'N/A')}")
        else:
            print(f"   ❌ Failed: {response.text}")
            
            # Additional debugging for 401 errors
            if response.status_code == 401:
                print(f"   - 401 Unauthorized - authentication issue at this level")
            elif response.status_code == 500:
                print(f"   - 500 Internal Server Error - server issue")
    
    # Test original endpoints for comparison
    print(f"\n🔍 Testing original endpoints for comparison...")
    
    original_endpoints = [
        "/users/me",
        "/reports"
    ]
    
    for endpoint in original_endpoints:
        print(f"\n🔍 Testing {endpoint}...")
        response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ Success!")
            if endpoint == "/users/me":
                data = response.json()
                print(f"   - User: {data.get('email', 'N/A')}")
            elif endpoint == "/reports":
                data = response.json()
                print(f"   - Total Reports: {data.get('total', 'N/A')}")
        else:
            print(f"   ❌ Failed: {response.text}")

if __name__ == "__main__":
    test_debug_endpoints()
