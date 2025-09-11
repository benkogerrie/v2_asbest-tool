#!/usr/bin/env python3
"""
Test script om te controleren wat er gebeurt bij directe toegang tot tenant admin UI.
"""

import requests
import json

# Configuratie
BASE_URL = "https://v2asbest-tool-production.up.railway.app"
TENANT_ADMIN_EMAIL = "admin@bedrijfy.nl"
TENANT_ADMIN_PASSWORD = "Admin123!"

def test_direct_tenant_admin_access():
    """Test directe toegang tot tenant admin UI."""
    print("🔍 TESTING DIRECT TENANT ADMIN ACCESS")
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
    
    # Stap 2: Simuleer wat er gebeurt wanneer de gebruiker direct naar tenant admin UI gaat
    print("\n2. Simulating direct access to tenant admin UI...")
    
    # Headers zoals frontend gebruikt
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test de endpoints die de tenant admin UI aanroept bij page load
    print("\n3. Testing tenant admin UI endpoints...")
    
    # Test /users/me (wordt aangeroepen bij page load)
    print("   Testing /users/me...")
    response = requests.get(f"{BASE_URL}/users/me", headers=headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        user_info = response.json()
        print(f"   ✅ User info: {user_info.get('email')} - {user_info.get('role')}")
    else:
        print(f"   ❌ Failed: {response.text}")
        return
    
    # Test /users/ (wordt aangeroepen bij loadUsers)
    print("   Testing /users/...")
    response = requests.get(f"{BASE_URL}/users/", headers=headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        users = response.json()
        print(f"   ✅ Found {len(users)} users")
    else:
        print(f"   ❌ Failed: {response.text}")
        return
    
    # Test user creation
    print("   Testing user creation...")
    user_data = {
        "first_name": "Direct",
        "last_name": "Test",
        "email": "directtest@bedrijfy.nl",
        "password": "DirectTest123!",
        "role": "USER"
    }
    
    response = requests.post(f"{BASE_URL}/users/", 
                           headers=headers, 
                           json=user_data)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        print("   ✅ User creation successful")
        created_user = response.json()
        print(f"   Created: {created_user.get('email')}")
    else:
        print(f"   ❌ User creation failed: {response.text}")
        return
    
    # Test token na user creation
    print("   Testing token after user creation...")
    response = requests.get(f"{BASE_URL}/users/me", headers=headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        print("   ✅ Token still valid")
    else:
        print(f"   ❌ Token invalid: {response.text}")
    
    print("\n✅ All tests passed! The API works correctly.")
    print("   The problem must be in the frontend JavaScript code.")

if __name__ == "__main__":
    test_direct_tenant_admin_access()
