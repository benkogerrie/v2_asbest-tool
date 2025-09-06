#!/usr/bin/env python3
"""
Test script to check if there's an import issue with Security or Authenticator.
"""
import requests
import json

# Railway API URL
API_BASE_URL = "https://v2asbest-tool-production.up.railway.app"

def test_import_issue():
    """Test if there's an import issue with Security or Authenticator."""
    try:
        print(f"🔍 Testing for import issues...")
        
        # Test if the issue is with the Security import
        print(f"\n🔍 Testing if the issue is with the Security import...")
        
        # Try to access an endpoint that should work
        response = requests.get(f"{API_BASE_URL}/users/me")
        print(f"   /users/me (no auth): {response.status_code}")
        
        if response.status_code == 401:
            print(f"      ✅ Expected 401 - endpoint requires auth")
        else:
            print(f"      ❌ Unexpected response - possible import issue")
        
        # Test with auth
        print(f"\n🔍 Testing with authentication...")
        
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
            try:
                error_data = response.json()
                print(f"      Error: {json.dumps(error_data, indent=6)}")
            except:
                print(f"      Raw error: {response.text}")
        
        # Test if the issue is with the custom dependencies
        print(f"\n🔍 Testing custom dependencies...")
        
        # Test /reports endpoint
        response = requests.get(
            f"{API_BASE_URL}/reports",
            headers={'Authorization': f'Bearer {token}'}
        )
        
        print(f"   /reports (with auth): {response.status_code}")
        
        if response.status_code == 401:
            print(f"      ❌ 401 Unauthorized - custom dependency still failing")
            try:
                error_data = response.json()
                print(f"      Error: {json.dumps(error_data, indent=6)}")
            except:
                print(f"      Raw error: {response.text}")
        elif response.status_code == 200:
            print(f"      ✅ /reports works - custom dependency fixed!")
        else:
            print(f"      ⚠️ Unexpected status: {response.status_code}")
        
        # Test if the issue is with the Security import specifically
        print(f"\n🔍 Testing if the issue is with the Security import specifically...")
        
        # Check if there are any error messages in the response
        if response.status_code == 401:
            print(f"      The 401 error suggests the Security import might not be working")
            print(f"      Possible issues:")
            print(f"      1. Security import not available in FastAPI version")
            print(f"      2. Authenticator import not available in FastAPI Users version")
            print(f"      3. Dependency injection not working correctly")
        
    except Exception as e:
        print(f"❌ Exception: {e}")

def main():
    """Main function."""
    print("🔍 IMPORT ISSUE TEST")
    print("=" * 25)
    
    test_import_issue()
    
    print(f"\n📊 IMPORT ISSUE SUMMARY")
    print("=" * 25)
    print("This test checks for import issues with Security or Authenticator")

if __name__ == "__main__":
    main()
