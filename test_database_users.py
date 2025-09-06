#!/usr/bin/env python3
"""
Test script to check if users exist in the database.
"""
import requests
import json

# Railway API URL
API_BASE_URL = "https://v2asbest-tool-production.up.railway.app"

# Test credentials
TEST_EMAIL = "admin@bedrijfy.nl"
TEST_PASSWORD = "Admin123!"
SYSTEM_EMAIL = "system@asbest-tool.nl"
SYSTEM_PASSWORD = "SystemOwner123!"

def test_user_exists(email, password, expected_role):
    """Test if a user exists and can login."""
    try:
        print(f"🔍 Testing user: {email}")
        
        response = requests.post(
            f"{API_BASE_URL}/auth/jwt/login",
            data={
                "username": email,
                "password": password
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print(f"   ✅ Login successful")
            
            # Get user info
            user_response = requests.get(
                f"{API_BASE_URL}/users/me",
                headers={'Authorization': f'Bearer {token}'}
            )
            
            if user_response.status_code == 200:
                user_data = user_response.json()
                print(f"   ✅ User exists in database:")
                print(f"      - ID: {user_data.get('id')}")
                print(f"      - Email: {user_data.get('email')}")
                print(f"      - Role: {user_data.get('role')}")
                print(f"      - Tenant ID: {user_data.get('tenant_id')}")
                print(f"      - Is Active: {user_data.get('is_active')}")
                print(f"      - Is Verified: {user_data.get('is_verified')}")
                
                if user_data.get('role') != expected_role:
                    print(f"   ⚠️ Role mismatch: expected {expected_role}, got {user_data.get('role')}")
                
                return True
            else:
                print(f"   ❌ Failed to get user info: {user_response.status_code}")
                return False
        else:
            print(f"   ❌ Login failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False

def test_register_endpoint():
    """Test if the register endpoint works."""
    try:
        print(f"\n🔍 Testing register endpoint...")
        
        # Try to register a test user
        test_user_data = {
            "email": "test@example.com",
            "password": "Test123!",
            "first_name": "Test",
            "last_name": "User"
        }
        
        response = requests.post(
            f"{API_BASE_URL}/auth/register",
            json=test_user_data
        )
        
        print(f"   Register endpoint: {response.status_code}")
        if response.status_code in [200, 201]:
            print(f"   ✅ Register endpoint works")
            return True
        else:
            print(f"   ❌ Register endpoint failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Register test exception: {e}")
        return False

def test_health_endpoints():
    """Test health endpoints to see if the API is working."""
    try:
        print(f"\n🔍 Testing health endpoints...")
        
        endpoints = [
            "/healthz",
            "/healthz/storage"
        ]
        
        for endpoint in endpoints:
            response = requests.get(f"{API_BASE_URL}{endpoint}")
            status_emoji = "✅" if response.status_code == 200 else "❌"
            print(f"   {status_emoji} {endpoint}: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"      Status: {data.get('status')}")
    
    except Exception as e:
        print(f"   ❌ Health test exception: {e}")

def main():
    """Main function."""
    print("🔍 DATABASE USERS TEST")
    print("=" * 30)
    
    # Test health endpoints first
    test_health_endpoints()
    
    # Test if users exist
    print(f"\n1. Testing if users exist in database...")
    
    users_to_test = [
        ("admin@bedrijfy.nl", "Admin123!", "ADMIN"),
        ("system@asbest-tool.nl", "SystemOwner123!", "SYSTEM_OWNER")
    ]
    
    existing_users = 0
    for email, password, expected_role in users_to_test:
        if test_user_exists(email, password, expected_role):
            existing_users += 1
        print()
    
    # Test register endpoint
    print(f"\n2. Testing register endpoint...")
    register_works = test_register_endpoint()
    
    # Summary
    print(f"\n📊 DATABASE USERS SUMMARY")
    print("=" * 30)
    print(f"Users found: {existing_users}/{len(users_to_test)}")
    print(f"Register endpoint: {'✅ Working' if register_works else '❌ Not working'}")
    
    if existing_users == 0:
        print(f"\n🚨 ISSUE: No users found in database!")
        print(f"   - The seed script may not have been run")
        print(f"   - Users may have been deleted")
        print(f"   - Database connection issues")
    elif existing_users < len(users_to_test):
        print(f"\n⚠️ PARTIAL ISSUE: Some users missing")
        print(f"   - Seed script may be incomplete")
        print(f"   - Some users may have been deleted")
    else:
        print(f"\n✅ All users exist in database")
        print(f"   - The issue is likely in the authorization logic")

if __name__ == "__main__":
    main()
