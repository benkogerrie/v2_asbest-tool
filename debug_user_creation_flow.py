#!/usr/bin/env python3
"""
Debug script om de exacte user creation flow te simuleren.
"""

import requests
import json

# Configuratie
BASE_URL = "https://v2asbest-tool-production.up.railway.app"
TENANT_ADMIN_EMAIL = "admin@bedrijfy.nl"
TENANT_ADMIN_PASSWORD = "Admin123!"

def debug_user_creation_flow():
    """Debug de exacte user creation flow."""
    print("🔍 DEBUGGING USER CREATION FLOW")
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
    
    # Stap 2: Test /users/me (wat de UI doet bij page load)
    print("\n2. Testing /users/me (UI page load)...")
    response = requests.get(f"{BASE_URL}/users/me", headers=headers)
    
    if response.status_code != 200:
        print(f"❌ /users/me failed: {response.status_code}")
        print(f"Response: {response.text}")
        return
    
    user_info = response.json()
    print(f"✅ /users/me successful - Role: {user_info.get('role')}, Tenant: {user_info.get('tenant_id')}")
    
    # Stap 3: Test /users/ (wat de UI doet bij loadUsers())
    print("\n3. Testing /users/ (UI loadUsers)...")
    response = requests.get(f"{BASE_URL}/users/", headers=headers)
    
    if response.status_code != 200:
        print(f"❌ /users/ failed: {response.status_code}")
        print(f"Response: {response.text}")
        return
    
    users = response.json()
    print(f"✅ /users/ successful - Found {len(users)} users")
    
    # Stap 4: Test user creation (exact zoals UI doet)
    print("\n4. Testing user creation (UI form submit)...")
    user_data = {
        "first_name": "Debug",
        "last_name": "Test",
        "email": "debugtest@bedrijfy.nl",
        "password": "DebugTest123!",
        "role": "USER"
        # Geen tenant_id - wordt automatisch ingevuld
    }
    
    print(f"User data: {json.dumps(user_data, indent=2)}")
    
    response = requests.post(f"{BASE_URL}/users/", 
                           headers=headers, 
                           json=user_data)
    
    print(f"User creation status: {response.status_code}")
    print(f"User creation response: {response.text}")
    
    if response.status_code == 200:
        print("✅ User creation successful")
        created_user = response.json()
        print(f"   Created user: {created_user.get('email')}")
        print(f"   Tenant ID: {created_user.get('tenant_id')}")
    else:
        print("❌ User creation failed")
        return
    
    # Stap 5: Test token validity after user creation
    print("\n5. Testing token validity after user creation...")
    response = requests.get(f"{BASE_URL}/users/me", headers=headers)
    
    if response.status_code == 200:
        print("✅ Token still valid after user creation")
    else:
        print(f"❌ Token invalid after user creation: {response.status_code}")
        print("   This explains why user gets logged out!")
        print(f"Response: {response.text}")
    
    # Stap 6: Test /users/ again after user creation
    print("\n6. Testing /users/ after user creation...")
    response = requests.get(f"{BASE_URL}/users/", headers=headers)
    
    if response.status_code == 200:
        users = response.json()
        print(f"✅ /users/ still works - Found {len(users)} users")
    else:
        print(f"❌ /users/ failed after user creation: {response.status_code}")
        print(f"Response: {response.text}")

if __name__ == "__main__":
    debug_user_creation_flow()
