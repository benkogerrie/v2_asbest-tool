#!/usr/bin/env python3
"""
Debug token and authentication issues.
"""

import requests
import json

BASE_URL = 'https://v2asbest-tool-production.up.railway.app'

def test_token_debug():
    """Debug token and authentication issues."""
    
    print("🔍 Debugging token and authentication...")
    
    # Get token
    print("\n🔍 Getting token...")
    response = requests.post(f"{BASE_URL}/auth/jwt/login", data={
        "username": "admin@bedrijfy.nl",
        "password": "Admin123!"
    })
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code}")
        return
    
    token = response.json().get('access_token')
    print(f"✅ Token received: {token[:50]}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test multiple times
    for i in range(3):
        print(f"\n🔍 Test {i+1}/3 - /reports...")
        response = requests.get(f"{BASE_URL}/reports", headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success - {data.get('total', 0)} reports")
        else:
            print(f"   ❌ Failed: {response.text}")
    
    # Test with different user
    print(f"\n🔍 Testing with system owner...")
    response = requests.post(f"{BASE_URL}/auth/jwt/login", data={
        "username": "system@asbest-tool.nl",
        "password": "SystemOwner123!"
    })
    
    if response.status_code == 200:
        token = response.json().get('access_token')
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(f"{BASE_URL}/reports", headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ System owner success - {data.get('total', 0)} reports")
        else:
            print(f"   ❌ System owner failed: {response.text}")
    else:
        print(f"   ❌ System owner login failed: {response.status_code}")

if __name__ == "__main__":
    test_token_debug()
