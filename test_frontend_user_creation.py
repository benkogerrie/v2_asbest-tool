#!/usr/bin/env python3
"""
Test script om te controleren wat er misgaat in de frontend user creation.
"""

import requests
import json

# Configuratie
BASE_URL = "https://v2asbest-tool-production.up.railway.app"
TENANT_ADMIN_EMAIL = "admin@bedrijfy.nl"
TENANT_ADMIN_PASSWORD = "Admin123!"

def test_frontend_user_creation():
    """Test de frontend user creation flow."""
    print("🧪 TESTING FRONTEND USER CREATION")
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
    
    # Stap 2: Simuleer de exacte frontend flow
    print("\n2. Simulating frontend user creation flow...")
    
    # Headers zoals frontend gebruikt
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # User data zoals frontend verzendt
    user_data = {
        "first_name": "Frontend",
        "last_name": "Test",
        "email": "frontendtest2@bedrijfy.nl",
        "password": "FrontendTest123!",
        "role": "USER"
    }
    
    print(f"Request headers: {json.dumps(headers, indent=2)}")
    print(f"Request body: {json.dumps(user_data, indent=2)}")
    
    # POST request zoals frontend doet
    response = requests.post(f"{BASE_URL}/users/", 
                           headers=headers, 
                           json=user_data)
    
    print(f"\nResponse status: {response.status_code}")
    print(f"Response headers: {dict(response.headers)}")
    print(f"Response body: {response.text}")
    
    if response.status_code == 200:
        print("✅ User creation successful")
        created_user = response.json()
        print(f"   Created user: {created_user.get('email')}")
        
        # Test token na user creation
        print("\n3. Testing token after user creation...")
        me_response = requests.get(f"{BASE_URL}/users/me", headers=headers)
        print(f"Token validity: {me_response.status_code}")
        
        if me_response.status_code == 200:
            print("✅ Token still valid")
        else:
            print(f"❌ Token invalid: {me_response.text}")
            
    else:
        print("❌ User creation failed")
        
        # Extra debugging
        print(f"\n🔍 DEBUG INFO:")
        print(f"   Request URL: {BASE_URL}/users/")
        print(f"   Request method: POST")
        print(f"   Request headers: {json.dumps(headers, indent=2)}")
        print(f"   Request body: {json.dumps(user_data, indent=2)}")
        print(f"   Response status: {response.status_code}")
        print(f"   Response headers: {dict(response.headers)}")
        print(f"   Response body: {response.text}")

if __name__ == "__main__":
    test_frontend_user_creation()
