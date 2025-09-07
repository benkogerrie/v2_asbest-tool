#!/usr/bin/env python3
"""
Test script om tenant creation te testen en foutmeldingen te identificeren
"""

import requests
import json

BASE_URL = "https://v2asbest-tool-production.up.railway.app"

def test_tenant_creation():
    print("🔍 Testing tenant creation...")
    
    # Login als System Owner
    login_data = {
        "username": "system@asbest-tool.nl",
        "password": "SystemOwner123!"
    }
    
    print(f"📝 Logging in as System Owner...")
    
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
    
    # Test tenant creation with minimal required fields
    print("\n🔍 Testing tenant creation with minimal fields...")
    minimal_tenant = {
        "tenant": {
            "name": "Test Bedrijf Minimal",
            "kvk": "87654321",
            "contact_email": "test@minimal.nl"
        },
        "admin": {
            "first_name": "Test",
            "last_name": "Admin",
            "email": "admin@minimal.nl",
            "role": "ADMIN"
        }
    }
    
    response = requests.post(f"{BASE_URL}/tenants/with-admin", json=minimal_tenant, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 201:
        result = response.json()
        print(f"✅ Tenant created successfully: {result.get('tenant', {}).get('name')}")
        print(f"✅ Admin created: {result.get('admin', {}).get('first_name')} {result.get('admin', {}).get('last_name')}")
        print(f"✅ Temp password: {result.get('temp_password')}")
    else:
        print(f"❌ Failed to create tenant: {response.status_code}")
        try:
            error_data = response.json()
            print(f"Error details: {json.dumps(error_data, indent=2)}")
        except:
            print(f"Raw error: {response.text}")
    
    # Test tenant creation with all fields (like UI would send)
    print("\n🔍 Testing tenant creation with all fields...")
    full_tenant = {
        "tenant": {
            "name": "Test Bedrijf Full",
            "kvk": "11223344",
            "contact_email": "info@full.nl",
            "phone": "+31 20 123 4567",
            "address": "Straat 1, 1234 AB Plaats",
            "website": "https://www.full.nl",
            "industry": "Bouw & Constructie"
        },
        "admin": {
            "first_name": "Jan",
            "last_name": "de Vries",
            "email": "jan@full.nl",
            "phone": "+31 6 123 45678",
            "job_title": "Project Manager",
            "department": "Bouw & Onderhoud",
            "role": "ADMIN"
        }
    }
    
    response = requests.post(f"{BASE_URL}/tenants/with-admin", json=full_tenant, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 201:
        result = response.json()
        print(f"✅ Tenant created successfully: {result.get('tenant', {}).get('name')}")
        print(f"✅ Admin created: {result.get('admin', {}).get('first_name')} {result.get('admin', {}).get('last_name')}")
        print(f"✅ Temp password: {result.get('temp_password')}")
    else:
        print(f"❌ Failed to create tenant: {response.status_code}")
        try:
            error_data = response.json()
            print(f"Error details: {json.dumps(error_data, indent=2)}")
        except:
            print(f"Raw error: {response.text}")

if __name__ == "__main__":
    test_tenant_creation()