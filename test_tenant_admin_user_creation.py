#!/usr/bin/env python3
"""
Test script om te controleren wat er mis gaat met tenant admin user creation.
"""

import requests
import json

# Configuratie
BASE_URL = "https://v2asbest-tool-production.up.railway.app"
TENANT_ADMIN_EMAIL = "admin@bedrijfy.nl"
TENANT_ADMIN_PASSWORD = "Admin123!"

def login_as_tenant_admin():
    """Login als tenant admin."""
    print("🔐 Logging in as tenant admin...")
    
    response = requests.post(f"{BASE_URL}/auth/jwt/login", data={
        "username": TENANT_ADMIN_EMAIL,
        "password": TENANT_ADMIN_PASSWORD
    })
    
    if response.status_code == 200:
        token = response.json().get('access_token')
        print("✅ Tenant admin login successful")
        return token
    else:
        print(f"❌ Tenant admin login failed: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def test_get_current_user(token):
    """Test de /users/me endpoint."""
    print("\n👤 Testing /users/me endpoint...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(f"{BASE_URL}/users/me", headers=headers)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        user_info = response.json()
        print("✅ /users/me successful")
        print(f"   Email: {user_info.get('email')}")
        print(f"   Role: {user_info.get('role')}")
        print(f"   Tenant ID: {user_info.get('tenant_id')}")
        print(f"   Tenant Name: {user_info.get('tenant_name')}")
        return user_info
    else:
        print(f"❌ /users/me failed: {response.text}")
        return None

def test_create_user(token, user_info):
    """Test user creation."""
    print("\n👥 Testing user creation...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    user_data = {
        "first_name": "Test",
        "last_name": "User",
        "email": "testuser@bedrijfy.nl",
        "password": "TestUser123!",
        "role": "USER",
        "tenant_id": user_info.get('tenant_id')
    }
    
    print(f"Creating user with tenant_id: {user_data['tenant_id']}")
    
    response = requests.post(f"{BASE_URL}/users/", 
                           headers=headers, 
                           json=user_data)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 201:
        created_user = response.json()
        print("✅ User creation successful")
        print(f"   Created user: {created_user.get('email')}")
        return True
    else:
        print(f"❌ User creation failed: {response.text}")
        return False

def main():
    print("🧪 Testing Tenant Admin User Creation")
    print("=" * 50)
    
    # Stap 1: Login als tenant admin
    token = login_as_tenant_admin()
    if not token:
        return
    
    # Stap 2: Test /users/me endpoint
    user_info = test_get_current_user(token)
    if not user_info:
        return
    
    # Stap 3: Test user creation
    success = test_create_user(token, user_info)
    
    if success:
        print("\n🎉 All tests passed!")
    else:
        print("\n❌ User creation failed")
    
    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    main()
