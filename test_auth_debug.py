#!/usr/bin/env python3
"""
Debug authentication issues with detailed logging.
"""

import requests
import json

BASE_URL = 'https://v2asbest-tool-production.up.railway.app'

def test_auth_debug():
    """Debug authentication with detailed logging."""
    
    print("🔍 Debugging authentication with detailed logging...")
    
    # Get token
    print("\n🔍 Getting token...")
    response = requests.post(f"{BASE_URL}/auth/jwt/login", data={
        "username": "admin@bedrijfy.nl",
        "password": "Admin123!"
    })
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code}")
        print(f"Response: {response.text}")
        return
    
    token = response.json().get('access_token')
    print(f"✅ Token received: {token[:50]}...")
    
    # Test /users/me first
    print("\n🔍 Testing /users/me...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/users/me", headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        user_data = response.json()
        print(f"   ✅ User: {user_data.get('email')} (Role: {user_data.get('role')})")
    else:
        print(f"   ❌ Failed: {response.text}")
        return
    
    # Test /reports with detailed headers
    print("\n🔍 Testing /reports with detailed headers...")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    response = requests.get(f"{BASE_URL}/reports", headers=headers)
    print(f"   Status: {response.status_code}")
    print(f"   Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Success - {data.get('total', 0)} reports")
    else:
        print(f"   ❌ Failed: {response.text}")
        
        # Try with different endpoint
        print("\n🔍 Trying /reports/ (with trailing slash)...")
        response = requests.get(f"{BASE_URL}/reports/", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success with trailing slash - {data.get('total', 0)} reports")
        else:
            print(f"   ❌ Still failed: {response.text}")

if __name__ == "__main__":
    test_auth_debug()
