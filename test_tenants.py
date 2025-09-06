#!/usr/bin/env python3
"""
Test script to check available tenants.
"""
import requests
import json

# Railway API URL
API_BASE_URL = "https://v2asbest-tool-production.up.railway.app"

# Test credentials
TEST_EMAIL = "system@asbest-tool.nl"
TEST_PASSWORD = "SystemOwner123!"

def login():
    """Login and get JWT token."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/jwt/login",
            data={
                "username": TEST_EMAIL,
                "password": TEST_PASSWORD
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print(f"✅ Login successful: {TEST_EMAIL}")
            return token
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def get_tenants(token):
    """Get available tenants."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/tenants",
            headers={'Authorization': f'Bearer {token}'}
        )
        
        if response.status_code == 200:
            tenants = response.json()
            print(f"✅ Found {len(tenants)} tenants:")
            for tenant in tenants:
                print(f"   - {tenant.get('name')} (ID: {tenant.get('id')})")
            return tenants
        else:
            print(f"❌ Failed to get tenants: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print(f"❌ Get tenants error: {e}")
        return []

def main():
    """Main function."""
    print("🔍 CHECKING AVAILABLE TENANTS")
    print("=" * 40)
    
    token = login()
    if not token:
        return
    
    tenants = get_tenants(token)
    
    if tenants:
        print(f"\n📋 Use one of these tenant IDs for testing:")
        for tenant in tenants:
            print(f"   {tenant.get('id')} - {tenant.get('name')}")
    else:
        print("\n❌ No tenants found")

if __name__ == "__main__":
    main()
