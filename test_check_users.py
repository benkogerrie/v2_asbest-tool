#!/usr/bin/env python3
"""
Test script to check what users exist in the database.
"""

import requests
import json

BASE_URL = 'https://v2asbest-tool-production.up.railway.app'

def check_users():
    """Check what users exist by trying different credentials."""
    
    print("🔍 Checking what users exist in the database...")
    
    # Try different possible credentials for S. Jansen
    possible_credentials = [
        {"username": "s.jansen@bedrijf-y.nl", "password": "temp_password_123"},
        {"username": "s.jansen@bedrijf-y.nl", "password": "password123"},
        {"username": "s.jansen@bedrijf-y.nl", "password": "admin123"},
        {"username": "s.jansen@bedrijf-y.nl", "password": "temp123"},
        {"username": "s.jansen@bedrijf-y.nl", "password": "123456"},
        {"username": "admin@bedrijf-y.nl", "password": "temp_password_123"},
        {"username": "admin@bedrijf-y.nl", "password": "password123"},
        {"username": "admin@bedrijf-y.nl", "password": "admin123"},
    ]
    
    for creds in possible_credentials:
        print(f"🔐 Trying {creds['username']} with password {creds['password']}...")
        
        try:
            response = requests.post(f"{BASE_URL}/auth/jwt/login", data=creds)
            if response.status_code == 200:
                print(f"✅ SUCCESS! Login worked for {creds['username']}")
                token_data = response.json()
                token = token_data.get('access_token')
                
                # Get user info
                headers = {"Authorization": f"Bearer {token}"}
                response = requests.get(f"{BASE_URL}/users/me", headers=headers)
                
                if response.status_code == 200:
                    user_info = response.json()
                    print(f"   - Name: {user_info.get('first_name')} {user_info.get('last_name')}")
                    print(f"   - Email: {user_info.get('email')}")
                    print(f"   - Role: {user_info.get('role')}")
                    print(f"   - Tenant ID: {user_info.get('tenant_id')}")
                    
                    # Test reports
                    response = requests.get(f"{BASE_URL}/reports", headers=headers)
                    if response.status_code == 200:
                        reports_data = response.json()
                        print(f"   - Reports visible: {reports_data.get('total', 0)}")
                    else:
                        print(f"   - Reports endpoint failed: {response.status_code}")
                
                return creds
            else:
                print(f"   ❌ Failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("❌ No working credentials found")
    return None

if __name__ == "__main__":
    check_users()
