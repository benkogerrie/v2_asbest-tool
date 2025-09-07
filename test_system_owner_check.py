#!/usr/bin/env python3
"""
Test script to check users as system owner.
"""

import requests
import json

BASE_URL = 'https://v2asbest-tool-production.up.railway.app'

def check_as_system_owner():
    """Check users as system owner."""
    
    print("🔍 Checking users as system owner...")
    
    # Try system owner credentials
    system_owner_creds = [
        {"username": "system@asbest-tool.nl", "password": "system123"},
        {"username": "admin@asbest-tool.nl", "password": "admin123"},
        {"username": "system@asbest-tool.nl", "password": "password123"},
        {"username": "system@asbest-tool.nl", "password": "temp_password_123"},
    ]
    
    for creds in system_owner_creds:
        print(f"🔐 Trying system owner: {creds['username']}...")
        
        try:
            response = requests.post(f"{BASE_URL}/auth/jwt/login", data=creds)
            if response.status_code == 200:
                print(f"✅ SUCCESS! System owner login worked")
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
                    
                    # Get all users
                    response = requests.get(f"{BASE_URL}/users", headers=headers)
                    if response.status_code == 200:
                        users_data = response.json()
                        print(f"\n👥 All users in system ({len(users_data)} total):")
                        for user in users_data:
                            print(f"   - {user.get('first_name')} {user.get('last_name')} ({user.get('email')}) - Role: {user.get('role')} - Tenant: {user.get('tenant_name', 'N/A')}")
                    
                    # Get all tenants
                    response = requests.get(f"{BASE_URL}/tenants", headers=headers)
                    if response.status_code == 200:
                        tenants_data = response.json()
                        print(f"\n🏢 All tenants in system ({len(tenants_data)} total):")
                        for tenant in tenants_data:
                            print(f"   - {tenant.get('name')} (ID: {tenant.get('id')}) - Users: {tenant.get('user_count', 0)}")
                    
                    # Get all reports
                    response = requests.get(f"{BASE_URL}/reports", headers=headers)
                    if response.status_code == 200:
                        reports_data = response.json()
                        print(f"\n📊 All reports in system ({reports_data.get('total', 0)} total):")
                        for report in reports_data.get('items', [])[:10]:  # Show first 10
                            print(f"   - {report.get('filename')} (Status: {report.get('status')}) - Tenant: {report.get('tenant_name', 'N/A')}")
                
                return creds
            else:
                print(f"   ❌ Failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("❌ No working system owner credentials found")
    return None

if __name__ == "__main__":
    check_as_system_owner()
