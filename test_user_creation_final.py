#!/usr/bin/env python3
"""
Test script om te controleren of de user creation fix volledig werkt.
"""

import requests
import json
import time

# Configuratie
BASE_URL = "https://v2asbest-tool-production.up.railway.app"
TENANT_ADMIN_EMAIL = "admin@bedrijfy.nl"
TENANT_ADMIN_PASSWORD = "Admin123!"

def test_user_creation_final():
    """Test of de user creation fix volledig werkt."""
    print("🧪 TESTING USER CREATION FINAL")
    print("=" * 60)
    
    # Stap 1: Login als tenant admin
    print("1. Logging in as tenant admin...")
    response = requests.post(f"{BASE_URL}/auth/jwt/login", data={
        "username": TENANT_ADMIN_EMAIL,
        "password": TENANT_ADMIN_PASSWORD
    })
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code}")
        return
    
    token = response.json().get('access_token')
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login successful")
    
    # Stap 2: Test user creation met unieke email
    print("\n2. Testing user creation with unique email...")
    timestamp = int(time.time())
    user_data = {
        "first_name": "Test",
        "last_name": "User",
        "email": f"testuser{timestamp}@bedrijfy.nl",
        "password": "TestUser123!",
        "role": "USER"
    }
    
    print(f"Creating user with email: {user_data['email']}")
    
    response = requests.post(f"{BASE_URL}/users/", 
                           headers=headers, 
                           json=user_data)
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("✅ User creation successful")
        created_user = response.json()
        print(f"   Created user: {created_user.get('email')}")
    else:
        print(f"❌ User creation failed: {response.status_code}")
        return
    
    # Stap 3: Test user creation met dezelfde email (moet 400 error geven)
    print("\n3. Testing user creation with duplicate email...")
    user_data = {
        "first_name": "Duplicate",
        "last_name": "User",
        "email": f"testuser{timestamp}@bedrijfy.nl",  # Same email as above
        "password": "DuplicateUser123!",
        "role": "USER"
    }
    
    response = requests.post(f"{BASE_URL}/users/", 
                           headers=headers, 
                           json=user_data)
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 400:
        print("✅ Duplicate email correctly rejected with 400 error")
        error_data = response.json()
        print(f"   Error message: {error_data.get('error', {}).get('message')}")
    else:
        print(f"❌ Expected 400 error, got {response.status_code}")
        return
    
    # Stap 4: Test token validity after both operations
    print("\n4. Testing token validity after operations...")
    response = requests.get(f"{BASE_URL}/users/me", headers=headers)
    
    if response.status_code == 200:
        print("✅ Token still valid after operations")
    else:
        print(f"❌ Token invalid: {response.status_code}")
        return
    
    print("\n🎉 All tests passed! User creation fix is working correctly.")
    print("   - New users can be created successfully")
    print("   - Duplicate emails are rejected with 400 error")
    print("   - No more 500 errors or user logout issues")

if __name__ == "__main__":
    test_user_creation_final()
