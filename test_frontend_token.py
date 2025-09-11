#!/usr/bin/env python3
"""
Test script om te controleren of de frontend token correct is.
"""

import requests
import json

# Configuratie
BASE_URL = "https://v2asbest-tool-production.up.railway.app"
TENANT_ADMIN_EMAIL = "admin@bedrijfy.nl"
TENANT_ADMIN_PASSWORD = "Admin123!"

def test_frontend_token_flow():
    """Test de exacte flow die de frontend gebruikt."""
    print("🧪 TESTING FRONTEND TOKEN FLOW")
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
    print("✅ Login successful")
    print(f"Token: {token}")
    
    # Stap 2: Test /users/me met exact dezelfde headers als frontend
    print("\n2. Testing /users/me with frontend-style headers...")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(f"{BASE_URL}/users/me", headers=headers)
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("✅ /users/me successful")
        user_info = response.json()
        print(f"User role: {user_info.get('role')}")
        print(f"User tenant: {user_info.get('tenant_id')}")
    else:
        print(f"❌ /users/me failed: {response.status_code}")
        
        # Test andere endpoints
        print("\n3. Testing /users/ endpoint...")
        users_response = requests.get(f"{BASE_URL}/users/", headers=headers)
        print(f"Users status: {users_response.status_code}")
        if users_response.status_code != 200:
            print(f"Users response: {users_response.text}")
    
    # Stap 4: Test user creation
    print("\n4. Testing user creation...")
    user_data = {
        "first_name": "Frontend",
        "last_name": "Test",
        "email": "frontendtest@bedrijfy.nl",
        "password": "FrontendTest123!",
        "role": "USER"
    }
    
    response = requests.post(f"{BASE_URL}/users/", 
                           headers=headers, 
                           json=user_data)
    
    print(f"User creation status: {response.status_code}")
    print(f"User creation response: {response.text}")
    
    if response.status_code == 200:
        print("✅ User creation successful")
    else:
        print("❌ User creation failed")
        
        # Test token validity after failed user creation
        print("\n5. Testing token validity after failed user creation...")
        me_response = requests.get(f"{BASE_URL}/users/me", headers=headers)
        print(f"Token validity status: {me_response.status_code}")

if __name__ == "__main__":
    test_frontend_token_flow()
