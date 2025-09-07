#!/usr/bin/env python3
"""
Test health check and basic API functionality.
"""

import requests
import json

BASE_URL = 'https://v2asbest-tool-production.up.railway.app'

def test_health_check():
    """Test health check and basic API functionality."""
    
    print("🔍 Testing health check and basic API functionality...")
    
    # Test health check
    print("\n🔍 Testing /healthz...")
    try:
        response = requests.get(f"{BASE_URL}/healthz", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ Health check OK: {response.json()}")
        else:
            print(f"   ❌ Health check failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
    
    # Test login
    print("\n🔍 Testing login...")
    try:
        response = requests.post(f"{BASE_URL}/auth/jwt/login", data={
            "username": "admin@bedrijfy.nl",
            "password": "Admin123!"
        }, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ Login successful")
            token = response.json().get('access_token')
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test /users/me
            print("\n🔍 Testing /users/me...")
            response = requests.get(f"{BASE_URL}/users/me", headers=headers, timeout=10)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   ✅ /users/me works")
            else:
                print(f"   ❌ /users/me failed: {response.text}")
            
            # Test /reports/ (with trailing slash)
            print("\n🔍 Testing /reports/...")
            response = requests.get(f"{BASE_URL}/reports/", headers=headers, timeout=10)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ /reports/ works - {data.get('total', 0)} reports found")
            else:
                print(f"   ❌ /reports/ failed: {response.text}")
                
        else:
            print(f"   ❌ Login failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Login error: {e}")

if __name__ == "__main__":
    test_health_check()
