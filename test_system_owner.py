#!/usr/bin/env python3
"""
Test script voor System Owner functionaliteit
"""

import requests
import json

BASE_URL = "https://v2asbest-tool-production.up.railway.app"

def test_system_owner():
    print("🔍 Testing System Owner functionality...")
    
    # Login als System Owner
    login_data = {
        "username": "system@asbest-tool.nl",
        "password": "SystemOwner123!"
    }
    
    print(f"📝 Logging in as System Owner: {login_data['username']}")
    
    response = requests.post(f"{BASE_URL}/auth/jwt/login", data=login_data)
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code}")
        print(f"Response: {response.text}")
        return
    
    token = response.json().get("access_token")
    if not token:
        print("❌ No access token received")
        return
    
    print("✅ Login successful")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 1: Check current user info
    print("\n🔍 Testing current user info...")
    response = requests.get(f"{BASE_URL}/users/me", headers=headers)
    if response.status_code == 200:
        user_info = response.json()
        print(f"✅ Current user: {user_info.get('email')} (Role: {user_info.get('role')})")
    else:
        print(f"❌ Failed to get user info: {response.status_code}")
    
    # Test 2: List existing tenants
    print("\n🔍 Testing tenant listing...")
    response = requests.get(f"{BASE_URL}/tenants/", headers=headers)
    if response.status_code == 200:
        tenants = response.json()
        if isinstance(tenants, list):
            print(f"✅ Found {len(tenants)} tenants")
            for tenant in tenants:
                print(f"   - {tenant.get('name')} (ID: {tenant.get('id')})")
        else:
            print(f"✅ Found {len(tenants.get('items', []))} tenants")
            for tenant in tenants.get('items', []):
                print(f"   - {tenant.get('name')} (ID: {tenant.get('id')})")
    else:
        print(f"❌ Failed to list tenants: {response.status_code}")
        print(f"Response: {response.text}")
    
    # Test 3: Create a new tenant
    print("\n🔍 Testing tenant creation...")
    new_tenant = {
        "name": "Test Bedrijf Z",
        "kvk": "12345678",
        "contact_email": "test@bedrijfz.nl",
        "phone": "+31 6 12345678",
        "description": "Test tenant voor System Owner functionaliteit"
    }
    
    response = requests.post(f"{BASE_URL}/tenants/", json=new_tenant, headers=headers)
    if response.status_code == 201:
        created_tenant = response.json()
        print(f"✅ Tenant created successfully: {created_tenant.get('name')} (ID: {created_tenant.get('id')})")
        
        # Test 4: Verify tenant was created
        print("\n🔍 Verifying tenant creation...")
        response = requests.get(f"{BASE_URL}/tenants/", headers=headers)
        if response.status_code == 200:
            tenants = response.json()
            if isinstance(tenants, list):
                print(f"✅ Now found {len(tenants)} tenants")
                for tenant in tenants:
                    print(f"   - {tenant.get('name')} (ID: {tenant.get('id')})")
            else:
                print(f"✅ Now found {len(tenants.get('items', []))} tenants")
                for tenant in tenants.get('items', []):
                    print(f"   - {tenant.get('name')} (ID: {tenant.get('id')})")
    else:
        print(f"❌ Failed to create tenant: {response.status_code}")
        print(f"Response: {response.text}")
    
    # Test 5: Test user management
    print("\n🔍 Testing user management...")
    response = requests.get(f"{BASE_URL}/users/", headers=headers)
    if response.status_code == 200:
        users = response.json()
        if isinstance(users, list):
            print(f"✅ Found {len(users)} users")
            for user in users:
                print(f"   - {user.get('email')} (Role: {user.get('role')}, Tenant: {user.get('tenant_name', 'N/A')})")
        else:
            print(f"✅ Found {len(users.get('items', []))} users")
            for user in users.get('items', []):
                print(f"   - {user.get('email')} (Role: {user.get('role')}, Tenant: {user.get('tenant_name', 'N/A')})")
    else:
        print(f"❌ Failed to list users: {response.status_code}")
        print(f"Response: {response.text}")

if __name__ == "__main__":
    test_system_owner()