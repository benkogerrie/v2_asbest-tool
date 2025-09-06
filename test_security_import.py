#!/usr/bin/env python3
"""
Test script to check if Security import is available in FastAPI 0.104.1.
"""
import requests
import json

# Railway API URL
API_BASE_URL = "https://v2asbest-tool-production.up.railway.app"

def test_security_import():
    """Test if Security import is available in FastAPI 0.104.1."""
    try:
        print(f"🔍 Testing Security import availability...")
        
        # Test if the issue is with the Security import
        print(f"\n🔍 Testing if the issue is with the Security import...")
        
        # Try to access the docs to see if there are any import errors
        response = requests.get(f"{API_BASE_URL}/docs")
        print(f"   /docs: {response.status_code}")
        
        if response.status_code == 200:
            print(f"      ✅ Docs endpoint works - no import errors")
        else:
            print(f"      ❌ Docs endpoint failed - possible import error")
        
        # Test if the issue is with the Authenticator import
        print(f"\n🔍 Testing if the issue is with the Authenticator import...")
        
        # Try to access an endpoint that should work
        response = requests.get(f"{API_BASE_URL}/healthz")
        print(f"   /healthz: {response.status_code}")
        
        if response.status_code == 200:
            print(f"      ✅ Health check works - basic FastAPI works")
        else:
            print(f"      ❌ Health check failed - possible import error")
        
        # Test if the issue is with the dependency injection
        print(f"\n🔍 Testing dependency injection...")
        
        # Login
        response = requests.post(
            f"{API_BASE_URL}/auth/jwt/login",
            data={
                "username": "admin@bedrijfy.nl",
                "password": "Admin123!"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code != 200:
            print(f"❌ Login failed: {response.status_code}")
            return
        
        token = response.json().get("access_token")
        print(f"✅ Login successful")
        
        # Test /users/me with auth
        response = requests.get(
            f"{API_BASE_URL}/users/me",
            headers={'Authorization': f'Bearer {token}'}
        )
        
        print(f"   /users/me (with auth): {response.status_code}")
        
        if response.status_code == 200:
            print(f"      ✅ /users/me works - FastAPI Users default works")
        else:
            print(f"      ❌ /users/me failed - possible import issue")
        
        # Test custom dependencies
        print(f"\n🔍 Testing custom dependencies...")
        
        # Test /reports endpoint
        response = requests.get(
            f"{API_BASE_URL}/reports",
            headers={'Authorization': f'Bearer {token}'}
        )
        
        print(f"   /reports (with auth): {response.status_code}")
        
        if response.status_code == 401:
            print(f"      ❌ 401 Unauthorized - custom dependency still failing")
            print(f"      Possible causes:")
            print(f"      1. Security import not available in FastAPI 0.104.1")
            print(f"      2. Authenticator import not available in FastAPI Users 12.1.3")
            print(f"      3. Dependency injection not working correctly")
            print(f"      4. Need to use different approach")
        elif response.status_code == 200:
            print(f"      ✅ /reports works - custom dependency fixed!")
        else:
            print(f"      ⚠️ Unexpected status: {response.status_code}")
        
    except Exception as e:
        print(f"❌ Exception: {e}")

def main():
    """Main function."""
    print("🔍 SECURITY IMPORT TEST")
    print("=" * 30)
    
    test_security_import()
    
    print(f"\n📊 SECURITY IMPORT SUMMARY")
    print("=" * 30)
    print("This test checks if Security import is available in FastAPI 0.104.1")

if __name__ == "__main__":
    main()
