#!/usr/bin/env python3
"""
Test script to try a simple fix approach.
"""
import requests
import json

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

def test_endpoints_with_simple_approach(token):
    """Test endpoints with a simple approach."""
    print(f"🔍 Testing endpoints with simple approach...")
    
    endpoints = [
        ("/users/me", "Should work"),
        ("/reports", "Should work with admin user"),
        ("/tenants", "Should work with system owner only"),
        ("/healthz", "Should work")
    ]
    
    for endpoint, description in endpoints:
        try:
            response = requests.get(
                f"{API_BASE_URL}{endpoint}",
                headers={'Authorization': f'Bearer {token}'}
            )
            
            status_emoji = "✅" if response.status_code in [200, 201] else "❌"
            print(f"   {status_emoji} {endpoint}: {response.status_code} - {description}")
            
            if response.status_code == 401:
                print(f"      ❌ 401 Unauthorized - Authentication issue")
            elif response.status_code == 403:
                print(f"      ⚠️ 403 Forbidden - Authorization issue (expected for some endpoints)")
            elif response.status_code in [200, 201]:
                print(f"      ✅ Success")
                
        except Exception as e:
            print(f"   ❌ {endpoint}: Exception - {e}")

def main():
    """Main function."""
    print("🔍 SIMPLE FIX TEST")
    print("=" * 30)
    
    # Login
    token = login()
    if not token:
        return
    
    # Test endpoints
    test_endpoints_with_simple_approach(token)
    
    print(f"\n📊 SIMPLE FIX SUMMARY")
    print("=" * 30)
    print("This test helps identify the exact issue")

if __name__ == "__main__":
    main()
