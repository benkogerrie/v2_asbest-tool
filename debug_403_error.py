#!/usr/bin/env python3
"""
Debug script om de 403 Forbidden error te onderzoeken.
"""

import requests
import json

# Configuratie
BASE_URL = "https://v2asbest-tool-production.up.railway.app"
TENANT_ADMIN_EMAIL = "admin@bedrijfy.nl"
TENANT_ADMIN_PASSWORD = "Admin123!"

def debug_403_error():
    """Debug de 403 Forbidden error."""
    print("🔍 DEBUGGING 403 FORBIDDEN ERROR")
    print("=" * 60)
    
    # Stap 1: Login als tenant admin
    print("1. Logging in as tenant admin...")
    response = requests.post(f"{BASE_URL}/auth/jwt/login", data={
        "username": TENANT_ADMIN_EMAIL,
        "password": TENANT_ADMIN_PASSWORD
    })
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code}")
        print(f"Response: {response.text}")
        return
    
    token = response.json().get('access_token')
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login successful")
    print(f"Token (first 50 chars): {token[:50]}...")
    
    # Stap 2: Test /users/me endpoint
    print("\n2. Testing /users/me endpoint...")
    response = requests.get(f"{BASE_URL}/users/me", headers=headers)
    
    print(f"Status: {response.status_code}")
    print(f"Response headers: {dict(response.headers)}")
    print(f"Response body: {response.text}")
    
    if response.status_code == 403:
        print("\n❌ 403 Forbidden - Let's check what's wrong...")
        
        # Test andere endpoints
        print("\n3. Testing /healthz endpoint...")
        health_response = requests.get(f"{BASE_URL}/healthz")
        print(f"Health status: {health_response.status_code}")
        
        # Test /users/ endpoint
        print("\n4. Testing /users/ endpoint...")
        users_response = requests.get(f"{BASE_URL}/users/", headers=headers)
        print(f"Users status: {users_response.status_code}")
        if users_response.status_code != 200:
            print(f"Users response: {users_response.text}")
        
        # Test token validity by decoding it
        print("\n5. Checking token structure...")
        try:
            import base64
            # JWT tokens have 3 parts separated by dots
            parts = token.split('.')
            if len(parts) == 3:
                # Decode the payload (second part)
                payload = parts[1]
                # Add padding if needed
                payload += '=' * (4 - len(payload) % 4)
                decoded = base64.b64decode(payload)
                payload_data = json.loads(decoded)
                print(f"Token payload: {json.dumps(payload_data, indent=2)}")
            else:
                print("❌ Invalid JWT token format")
        except Exception as e:
            print(f"❌ Error decoding token: {e}")
    
    elif response.status_code == 200:
        print("✅ /users/me successful")
        user_info = response.json()
        print(f"User info: {json.dumps(user_info, indent=2)}")
    else:
        print(f"❌ Unexpected status: {response.status_code}")

if __name__ == "__main__":
    debug_403_error()
