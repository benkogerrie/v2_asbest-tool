#!/usr/bin/env python3
"""
Test script to test FastAPI Users configuration.
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

def test_fastapi_users_endpoints(token):
    """Test FastAPI Users specific endpoints."""
    print(f"🔍 Testing FastAPI Users endpoints...")
    
    # Test the /users/me endpoint which should work
    try:
        response = requests.get(
            f"{API_BASE_URL}/users/me",
            headers={'Authorization': f'Bearer {token}'}
        )
        
        print(f"   /users/me: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ User data retrieved successfully")
            print(f"      - ID: {data.get('id')}")
            print(f"      - Email: {data.get('email')}")
            print(f"      - Role: {data.get('role')}")
            return True
        else:
            print(f"   ❌ Failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False

def test_custom_endpoints(token):
    """Test custom endpoints that use FastAPI Users dependencies."""
    print(f"\n🔍 Testing custom endpoints with FastAPI Users dependencies...")
    
    endpoints = [
        ("/reports", "Uses get_current_active_user"),
        ("/tenants", "Uses get_current_system_owner"),
        ("/analyses/reports/test-id/analysis", "Uses get_current_active_user"),
        ("/findings/reports/test-id/findings", "Uses get_current_active_user")
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
                print(f"      ❌ 401 Unauthorized - FastAPI Users dependency issue")
            elif response.status_code == 422:
                print(f"      ⚠️ 422 Validation Error - Expected for invalid UUID")
            elif response.status_code in [200, 201]:
                print(f"      ✅ Success - FastAPI Users dependency working")
                
        except Exception as e:
            print(f"   ❌ {endpoint}: Exception - {e}")

def test_different_auth_backends():
    """Test if there are multiple auth backends configured."""
    print(f"\n🔍 Testing different authentication methods...")
    
    # Test with different header formats
    token = login()
    if not token:
        return
    
    header_formats = [
        ("Bearer", f"Bearer {token}"),
        ("bearer", f"bearer {token}"),
        ("BEARER", f"BEARER {token}"),
        ("Authorization", f"Authorization: Bearer {token}"),
    ]
    
    for header_name, header_value in header_formats:
        try:
            response = requests.get(
                f"{API_BASE_URL}/users/me",
                headers={header_name: header_value}
            )
            
            status_emoji = "✅" if response.status_code == 200 else "❌"
            print(f"   {status_emoji} {header_name}: {response.status_code}")
            
        except Exception as e:
            print(f"   ❌ {header_name}: Exception - {e}")

def main():
    """Main function."""
    print("🔍 FASTAPI USERS CONFIGURATION TEST")
    print("=" * 50)
    
    # Login
    token = login()
    if not token:
        return
    
    # Test FastAPI Users endpoints
    print(f"\n1. Testing FastAPI Users endpoints...")
    users_working = test_fastapi_users_endpoints(token)
    
    # Test custom endpoints
    print(f"\n2. Testing custom endpoints...")
    test_custom_endpoints(token)
    
    # Test different auth methods
    print(f"\n3. Testing different authentication methods...")
    test_different_auth_backends()
    
    # Summary
    print(f"\n📊 FASTAPI USERS TEST SUMMARY")
    print("=" * 50)
    
    if users_working:
        print(f"✅ FastAPI Users basic functionality works")
        print(f"   - JWT token validation works")
        print(f"   - /users/me endpoint works")
        print(f"   - Issue is likely in custom dependency functions")
    else:
        print(f"❌ FastAPI Users basic functionality broken")
        print(f"   - JWT token validation not working")
        print(f"   - /users/me endpoint not working")
        print(f"   - Issue is in FastAPI Users configuration")
    
    print(f"\n🔧 POSSIBLE SOLUTIONS:")
    print(f"   1. Check FastAPI Users dependency injection")
    print(f"   2. Verify database session configuration")
    print(f"   3. Check JWT strategy configuration")
    print(f"   4. Verify User model compatibility")

if __name__ == "__main__":
    main()
