#!/usr/bin/env python3
"""
Test script to check schema compatibility with FastAPI Users.
"""
import requests
import json

# Railway API URL
API_BASE_URL = "https://v2asbest-tool-production.up.railway.app"

# Test credentials
TEST_EMAIL = "admin@bedrijfy.nl"
TEST_PASSWORD = "Admin123!"

def test_schema_compatibility():
    """Test if the issue is related to schema compatibility."""
    try:
        print(f"🔍 Testing schema compatibility...")
        
        # Login
        response = requests.post(
            f"{API_BASE_URL}/auth/jwt/login",
            data={
                "username": TEST_EMAIL,
                "password": TEST_PASSWORD
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code != 200:
            print(f"❌ Login failed: {response.status_code}")
            return
        
        token = response.json().get("access_token")
        print(f"✅ Login successful")
        
        # Test /users/me to see the schema structure
        print(f"\n🔍 Testing /users/me schema structure...")
        
        response = requests.get(
            f"{API_BASE_URL}/users/me",
            headers={'Authorization': f'Bearer {token}'}
        )
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ /users/me successful")
            print(f"   Schema structure:")
            for key, value in user_data.items():
                print(f"      {key}: {type(value).__name__} = {value}")
        else:
            print(f"❌ /users/me failed: {response.status_code}")
            return
        
        # Test register endpoint to see if it works
        print(f"\n🔍 Testing register endpoint...")
        
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
        else:
            print(f"   ❌ Register endpoint failed: {response.text}")
        
        # Test if the issue is with the FastAPI Users configuration
        print(f"\n🔍 Testing FastAPI Users configuration...")
        
        # Check if the issue is with the dependency injection
        print(f"   Testing dependency injection pattern...")
        
        # Test a simple endpoint that should work
        response = requests.get(
            f"{API_BASE_URL}/healthz",
            headers={'Authorization': f'Bearer {token}'}
        )
        
        print(f"   /healthz with auth: {response.status_code}")
        
        # Test without auth
        response = requests.get(f"{API_BASE_URL}/healthz")
        print(f"   /healthz without auth: {response.status_code}")
        
    except Exception as e:
        print(f"❌ Exception: {e}")

def test_fastapi_users_routes():
    """Test FastAPI Users specific routes."""
    try:
        print(f"\n🔍 Testing FastAPI Users routes...")
        
        # Test auth routes
        routes = [
            "/auth/jwt/login",
            "/auth/register",
            "/auth/verify",
            "/auth/forgot-password",
            "/auth/reset-password"
        ]
        
        for route in routes:
            try:
                if route == "/auth/jwt/login":
                    # This is a POST route
                    response = requests.post(
                        f"{API_BASE_URL}{route}",
                        data={
                            "username": TEST_EMAIL,
                            "password": TEST_PASSWORD
                        },
                        headers={"Content-Type": "application/x-www-form-urlencoded"}
                    )
                else:
                    # These are GET routes
                    response = requests.get(f"{API_BASE_URL}{route}")
                
                print(f"   {route}: {response.status_code}")
                
            except Exception as e:
                print(f"   {route}: Exception - {e}")
        
    except Exception as e:
        print(f"❌ Exception: {e}")

def main():
    """Main function."""
    print("🔍 SCHEMA COMPATIBILITY TEST")
    print("=" * 40)
    
    test_schema_compatibility()
    test_fastapi_users_routes()
    
    print(f"\n📊 SCHEMA COMPATIBILITY SUMMARY")
    print("=" * 40)
    print("This test helps identify if the issue is related to schema compatibility")

if __name__ == "__main__":
    main()
