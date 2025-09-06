#!/usr/bin/env python3
"""
Test script to check user information and tenant access.
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

def get_user_info(token):
    """Get current user information."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/users/me",
            headers={'Authorization': f'Bearer {token}'}
        )
        
        print(f"🔍 User info request")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ User data:")
            print(f"   - ID: {data.get('id')}")
            print(f"   - Email: {data.get('email')}")
            print(f"   - Role: {data.get('role')}")
            print(f"   - Tenant ID: {data.get('tenant_id')}")
            print(f"   - Is Active: {data.get('is_active')}")
            print(f"   - First Name: {data.get('first_name')}")
            print(f"   - Last Name: {data.get('last_name')}")
            return data
        else:
            print(f"   ❌ Error: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return None

def test_reports_with_debug(token):
    """Test reports endpoint with detailed debugging."""
    try:
        print(f"\n🔍 Testing reports endpoint with debug info")
        
        response = requests.get(
            f"{API_BASE_URL}/reports",
            headers={'Authorization': f'Bearer {token}'}
        )
        
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success: {len(data.get('items', []))} reports found")
            return data
        else:
            print(f"   ❌ Error: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return None

def main():
    """Main function."""
    print("🔍 USER INFO & AUTHORIZATION DEBUG")
    print("=" * 50)
    
    # Login
    token = login()
    if not token:
        return
    
    # Get user info
    print("\n1. Getting user information...")
    user_info = get_user_info(token)
    
    if user_info:
        print(f"\n2. Testing reports endpoint...")
        test_reports_with_debug(token)
    
    print("\n📊 DEBUG SUMMARY")
    print("=" * 50)
    print("This helps identify authorization issues")

if __name__ == "__main__":
    main()
