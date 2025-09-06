#!/usr/bin/env python3
"""
Test script to validate JWT token with FastAPI Users.
"""
import requests
import json
import base64
from datetime import datetime

# Railway API URL
API_BASE_URL = "https://v2asbest-tool-production.up.railway.app"

# Test credentials
TEST_EMAIL = "admin@bedrijfy.nl"
TEST_PASSWORD = "Admin123!"

def login():
    """Login and get JWT token."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/jwt/login",
            data={
                "username": TEST_EMAIL,
                "password": TEST_PASSWORD
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print(f"✅ Login successful: {TEST_EMAIL}")
            return token
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_jwt_validation_endpoint(token):
    """Test the JWT validation endpoint."""
    try:
        print(f"🔍 Testing JWT validation endpoint...")
        
        # Test the /users/me endpoint which should work
        response = requests.get(
            f"{API_BASE_URL}/users/me",
            headers={'Authorization': f'Bearer {token}'}
        )
        
        print(f"   /users/me: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ User validated: {data.get('email')} (Role: {data.get('role')})")
            return True
        else:
            print(f"   ❌ JWT validation failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False

def test_different_auth_headers(token):
    """Test different authorization header formats."""
    print(f"\n🔍 Testing different authorization header formats...")
    
    header_formats = [
        f"Bearer {token}",
        f"bearer {token}",
        f"BEARER {token}",
        token,  # Without Bearer prefix
    ]
    
    for header_format in header_formats:
        try:
            response = requests.get(
                f"{API_BASE_URL}/users/me",
                headers={'Authorization': header_format}
            )
            
            status_emoji = "✅" if response.status_code == 200 else "❌"
            print(f"   {status_emoji} '{header_format[:20]}...': {response.status_code}")
            
        except Exception as e:
            print(f"   ❌ '{header_format[:20]}...': Exception - {e}")

def test_cors_headers(token):
    """Test CORS headers and preflight requests."""
    print(f"\n🔍 Testing CORS headers...")
    
    try:
        # Test preflight request
        response = requests.options(
            f"{API_BASE_URL}/reports",
            headers={
                'Origin': 'http://localhost:3000',
                'Access-Control-Request-Method': 'GET',
                'Access-Control-Request-Headers': 'Authorization'
            }
        )
        
        print(f"   OPTIONS /reports: {response.status_code}")
        print(f"   CORS headers: {dict(response.headers)}")
        
    except Exception as e:
        print(f"   ❌ CORS test exception: {e}")

def main():
    """Main function."""
    print("🔍 JWT VALIDATION TEST")
    print("=" * 30)
    
    # Login
    token = login()
    if not token:
        return
    
    # Test JWT validation
    print(f"\n1. Testing JWT validation...")
    jwt_valid = test_jwt_validation_endpoint(token)
    
    if jwt_valid:
        # Test different header formats
        print(f"\n2. Testing different header formats...")
        test_different_auth_headers(token)
        
        # Test CORS
        print(f"\n3. Testing CORS...")
        test_cors_headers(token)
    
    print("\n📊 JWT VALIDATION SUMMARY")
    print("=" * 30)
    print("This helps identify JWT token validation issues")

if __name__ == "__main__":
    main()
