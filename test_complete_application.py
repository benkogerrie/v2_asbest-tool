#!/usr/bin/env python3
"""
Complete application test - test all major functionality.
"""

import requests
import json

BASE_URL = 'https://v2asbest-tool-production.up.railway.app'

def test_complete_application():
    """Test complete application functionality."""
    
    print("🔍 COMPLETE APPLICATION TEST")
    print("=" * 50)
    
    # Test 1: Health Check
    print("\n1️⃣ HEALTH CHECK")
    try:
        response = requests.get(f"{BASE_URL}/healthz", timeout=10)
        if response.status_code == 200:
            print("   ✅ API is healthy")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        return
    
    # Test 2: Login Tests
    print("\n2️⃣ LOGIN TESTS")
    
    # Test tenant admin login
    print("   🔍 Testing tenant admin login...")
    response = requests.post(f"{BASE_URL}/auth/jwt/login", data={
        "username": "admin@bedrijfy.nl",
        "password": "Admin123!"
    })
    
    if response.status_code == 200:
        admin_token = response.json().get('access_token')
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        print("   ✅ Tenant admin login successful")
    else:
        print(f"   ❌ Tenant admin login failed: {response.status_code}")
        return
    
    # Test system owner login
    print("   🔍 Testing system owner login...")
    response = requests.post(f"{BASE_URL}/auth/jwt/login", data={
        "username": "system@asbest-tool.nl",
        "password": "SystemOwner123!"
    })
    
    if response.status_code == 200:
        system_token = response.json().get('access_token')
        system_headers = {"Authorization": f"Bearer {system_token}"}
        print("   ✅ System owner login successful")
    else:
        print(f"   ❌ System owner login failed: {response.status_code}")
        return
    
    # Test 3: User Management
    print("\n3️⃣ USER MANAGEMENT")
    
    # Test /users/me for tenant admin
    print("   🔍 Testing /users/me for tenant admin...")
    response = requests.get(f"{BASE_URL}/users/me", headers=admin_headers)
    if response.status_code == 200:
        user_data = response.json()
        print(f"   ✅ Tenant admin: {user_data.get('email')} (Role: {user_data.get('role')})")
    else:
        print(f"   ❌ Tenant admin /users/me failed: {response.status_code}")
    
    # Test /users/me for system owner
    print("   🔍 Testing /users/me for system owner...")
    response = requests.get(f"{BASE_URL}/users/me", headers=system_headers)
    if response.status_code == 200:
        user_data = response.json()
        print(f"   ✅ System owner: {user_data.get('email')} (Role: {user_data.get('role')})")
    else:
        print(f"   ❌ System owner /users/me failed: {response.status_code}")
    
    # Test 4: Reports Management
    print("\n4️⃣ REPORTS MANAGEMENT")
    
    # Test /reports/ for tenant admin (with trailing slash)
    print("   🔍 Testing /reports/ for tenant admin...")
    response = requests.get(f"{BASE_URL}/reports/", headers=admin_headers)
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Tenant admin reports: {data.get('total', 0)} reports found")
    else:
        print(f"   ❌ Tenant admin reports failed: {response.status_code} - {response.text}")
    
    # Test /reports/ for system owner
    print("   🔍 Testing /reports/ for system owner...")
    response = requests.get(f"{BASE_URL}/reports/", headers=system_headers)
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ System owner reports: {data.get('total', 0)} reports found")
    else:
        print(f"   ❌ System owner reports failed: {response.status_code} - {response.text}")
    
    # Test 5: Tenant Management (System Owner only)
    print("\n5️⃣ TENANT MANAGEMENT")
    
    print("   🔍 Testing /tenants/ for system owner...")
    response = requests.get(f"{BASE_URL}/tenants/", headers=system_headers)
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ System owner tenants: {len(data)} tenants found")
    else:
        print(f"   ❌ System owner tenants failed: {response.status_code} - {response.text}")
    
    # Test tenant admin access to tenants (should fail)
    print("   🔍 Testing /tenants/ for tenant admin (should fail)...")
    response = requests.get(f"{BASE_URL}/tenants/", headers=admin_headers)
    if response.status_code == 403:
        print("   ✅ Tenant admin correctly denied access to tenants")
    else:
        print(f"   ❌ Tenant admin access to tenants: {response.status_code} - {response.text}")
    
    # Test 6: User Management (System Owner only)
    print("\n6️⃣ USER MANAGEMENT (SYSTEM OWNER)")
    
    print("   🔍 Testing /users/ for system owner...")
    response = requests.get(f"{BASE_URL}/users/", headers=system_headers)
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ System owner users: {len(data)} users found")
    else:
        print(f"   ❌ System owner users failed: {response.status_code} - {response.text}")
    
    # Test tenant admin access to all users (should fail)
    print("   🔍 Testing /users/ for tenant admin (should fail)...")
    response = requests.get(f"{BASE_URL}/users/", headers=admin_headers)
    if response.status_code == 403:
        print("   ✅ Tenant admin correctly denied access to all users")
    else:
        print(f"   ❌ Tenant admin access to all users: {response.status_code} - {response.text}")
    
    print("\n" + "=" * 50)
    print("🎉 COMPLETE APPLICATION TEST FINISHED")
    print("=" * 50)

if __name__ == "__main__":
    test_complete_application()
