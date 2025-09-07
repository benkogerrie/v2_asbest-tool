#!/usr/bin/env python3
"""
Show all users with their credentials and roles.
"""

import requests
import json

BASE_URL = 'https://v2asbest-tool-production.up.railway.app'

def show_users():
    """Show all users with their credentials and roles."""
    
    print("🔍 SHOWING ALL USERS")
    print("=" * 80)
    
    # Login as system owner to see all users
    response = requests.post(f"{BASE_URL}/auth/jwt/login", data={
        "username": "system@asbest-tool.nl",
        "password": "SystemOwner123!"
    })
    
    if response.status_code != 200:
        print(f"❌ System owner login failed: {response.status_code}")
        return
    
    token = response.json().get('access_token')
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get all users
    response = requests.get(f"{BASE_URL}/users/", headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Failed to get users: {response.status_code}")
        return
    
    users = response.json()
    
    print(f"📊 Total Users: {len(users)}")
    print("=" * 80)
    
    for i, user in enumerate(users, 1):
        print(f"\n{i}. 👤 {user.get('first_name', '')} {user.get('last_name', '')}")
        print(f"   Email: {user.get('email', 'Unknown')}")
        print(f"   Role: {user.get('role', 'Unknown')}")
        print(f"   Tenant: {user.get('tenant_name', 'N/A')}")
        print(f"   Active: {user.get('is_active', False)}")
        print(f"   Verified: {user.get('is_verified', False)}")
        print(f"   Created: {user.get('created_at', 'Unknown')}")
        print("-" * 60)
    
    print(f"\n🔑 KNOWN CREDENTIALS:")
    print("=" * 40)
    print("System Owner:")
    print("  Email: system@asbest-tool.nl")
    print("  Password: SystemOwner123!")
    print("  Role: SYSTEM_OWNER")
    print()
    print("Tenant Admin:")
    print("  Email: admin@bedrijfy.nl")
    print("  Password: Admin123!")
    print("  Role: ADMIN")
    print("  Tenant: Bedrijf Y")
    print()
    print("🎉 Total: {len(users)} users displayed")

if __name__ == "__main__":
    show_users()
