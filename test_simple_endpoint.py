#!/usr/bin/env python3
"""
Test the new test-simple endpoint to isolate routing issues.
"""

import requests
import json

BASE_URL = 'https://v2asbest-tool-production.up.railway.app'

def test_simple_endpoint():
    """Test the new test-simple endpoint."""
    
    print("🔍 Testing new test-simple endpoint...")
    
    # Test without authentication first
    print("\n🔍 Testing /reports/test-simple WITHOUT authentication...")
    response = requests.get(f"{BASE_URL}/reports/test-simple")
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        print(f"   ✅ Success! Response: {response.json()}")
    else:
        print(f"   ❌ Failed: {response.text}")
    
    # Test with authentication
    print("\n🔍 Testing /reports/test-simple WITH authentication...")
    
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
    
    # Test with auth
    response = requests.get(f"{BASE_URL}/reports/test-simple", headers=headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        print(f"   ✅ Success! Response: {response.json()}")
    else:
        print(f"   ❌ Failed: {response.text}")
    
    # Compare with original /reports/ endpoint
    print("\n🔍 Comparing with original /reports/ endpoint...")
    response = requests.get(f"{BASE_URL}/reports/", headers=headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        print(f"   ✅ Success! Response: {response.json()}")
    else:
        print(f"   ❌ Failed: {response.text}")

if __name__ == "__main__":
    test_simple_endpoint()
