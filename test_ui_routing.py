#!/usr/bin/env python3
"""
Test script om te controleren hoe de UI routing werkt na login
"""

import requests
import json

BASE_URL = "https://v2asbest-tool-production.up.railway.app"

def test_user_roles():
    print("🔍 Testing user roles and UI routing...")
    
    # Test alle gebruikersrollen
    users = [
        {
            "name": "System Owner",
            "email": "system@asbest-tool.nl",
            "password": "SystemOwner123!",
            "expected_role": "SYSTEM_OWNER"
        },
        {
            "name": "Tenant Admin",
            "email": "admin@bedrijfy.nl", 
            "password": "Admin123!",
            "expected_role": "ADMIN"
        }
    ]
    
    for user in users:
        print(f"\n📝 Testing {user['name']}...")
        
        # Login
        login_data = {
            "username": user["email"],
            "password": user["password"]
        }
        
        response = requests.post(f"{BASE_URL}/auth/jwt/login", data=login_data)
        
        if response.status_code != 200:
            print(f"❌ Login failed: {response.status_code}")
            continue
            
        token = response.json().get("access_token")
        if not token:
            print("❌ No access token received")
            continue
            
        print("✅ Login successful")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get user info
        response = requests.get(f"{BASE_URL}/users/me", headers=headers)
        if response.status_code == 200:
            user_info = response.json()
            actual_role = user_info.get('role')
            print(f"✅ User role: {actual_role}")
            
            if actual_role == user["expected_role"]:
                print(f"✅ Role matches expected: {user['expected_role']}")
            else:
                print(f"❌ Role mismatch! Expected: {user['expected_role']}, Got: {actual_role}")
                
            # Check what UI should show
            if actual_role == "SYSTEM_OWNER":
                print("🎯 Should show: System Owner UI (tenant management, user management, all reports)")
            elif actual_role == "ADMIN":
                print("🎯 Should show: Tenant Admin UI (tenant reports, user management within tenant)")
            elif actual_role == "USER":
                print("🎯 Should show: User UI (own tenant reports only)")
            else:
                print(f"❓ Unknown role: {actual_role}")
                
        else:
            print(f"❌ Failed to get user info: {response.status_code}")

if __name__ == "__main__":
    test_user_roles()
