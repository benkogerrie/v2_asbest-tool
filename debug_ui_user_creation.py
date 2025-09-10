#!/usr/bin/env python3
"""
Debug script om te controleren wat er misgaat met UI user creation.
"""

import requests
import json

# Configuratie
BASE_URL = "https://v2asbest-tool-production.up.railway.app"
TENANT_ADMIN_EMAIL = "admin@bedrijfy.nl"
TENANT_ADMIN_PASSWORD = "Admin123!"

def test_ui_user_creation_flow():
    """Test de exacte flow die de UI gebruikt."""
    print("🧪 DEBUGGING UI USER CREATION FLOW")
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
    
    # Stap 2: Test /users/me endpoint (wat de UI gebruikt)
    print("\n2. Testing /users/me endpoint...")
    response = requests.get(f"{BASE_URL}/users/me", headers=headers)
    
    if response.status_code != 200:
        print(f"❌ /users/me failed: {response.status_code}")
        return
    
    user_info = response.json()
    print(f"✅ /users/me successful - Role: {user_info.get('role')}, Tenant: {user_info.get('tenant_id')}")
    
    # Stap 3: Test user creation (exact zoals UI doet)
    print("\n3. Testing user creation (UI style)...")
    user_data = {
        "first_name": "UI",
        "last_name": "Test",
        "email": "uitest2@bedrijfy.nl",
        "password": "UITest123!",
        "role": "USER"
        # Geen tenant_id - wordt automatisch ingevuld
    }
    
    print(f"User data: {json.dumps(user_data, indent=2)}")
    
    response = requests.post(f"{BASE_URL}/users/", 
                           headers=headers, 
                           json=user_data)
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("✅ User creation successful")
        created_user = response.json()
        print(f"   Created user: {created_user.get('email')}")
        print(f"   Tenant ID: {created_user.get('tenant_id')}")
    else:
        print("❌ User creation failed")
        
        # Extra debugging
        print(f"\n🔍 DEBUG INFO:")
        print(f"   Request headers: {dict(headers)}")
        print(f"   Request body: {json.dumps(user_data, indent=2)}")
        print(f"   Response headers: {dict(response.headers)}")
    
    # Stap 4: Test of token nog geldig is na user creation
    print("\n4. Testing token validity after user creation...")
    response = requests.get(f"{BASE_URL}/users/me", headers=headers)
    
    if response.status_code == 200:
        print("✅ Token still valid after user creation")
    else:
        print(f"❌ Token invalid after user creation: {response.status_code}")
        print("   This explains why user gets logged out!")

if __name__ == "__main__":
    test_ui_user_creation_flow()
