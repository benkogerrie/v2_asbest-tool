#!/usr/bin/env python3
"""
Detailed analysis of specific endpoints
"""
import requests
import json

BASE_URL = 'https://v2asbest-tool-production.up.railway.app'

def test_system_owner_endpoints():
    """Test system owner specific endpoints"""
    print('🔍 DETAILED ENDPOINT ANALYSIS')
    print('=' * 50)

    # Login as system owner
    login_data = {
        'username': 'system@asbest-tool.nl',
        'password': 'SystemOwner123!'
    }

    response = requests.post(f'{BASE_URL}/auth/jwt/login', data=login_data)
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data['access_token']
        print('✅ System owner login successful')
        
        headers = {'Authorization': f'Bearer {access_token}'}
        
        # Test /tenants/my endpoint
        print('\nTesting /tenants/my endpoint:')
        response = requests.get(f'{BASE_URL}/tenants/my', headers=headers)
        print(f'Status: {response.status_code}')
        print(f'Response: {response.text}')
        
        # Test /users/me endpoint
        print('\nTesting /users/me endpoint:')
        response = requests.get(f'{BASE_URL}/users/me', headers=headers)
        print(f'Status: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            print(f'User: {data.get("email")} (Role: {data.get("role")})')
            print(f'Tenant ID: {data.get("tenant_id")}')
        
        # Test /tenants/ endpoint
        print('\nTesting /tenants/ endpoint:')
        response = requests.get(f'{BASE_URL}/tenants/', headers=headers)
        print(f'Status: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            print(f'Found {len(data)} tenants')
            for tenant in data:
                print(f'  - {tenant.get("name")} (ID: {tenant.get("id")})')
        
    else:
        print('❌ Login failed')

def test_admin_endpoints():
    """Test admin specific endpoints"""
    print('\n🔍 ADMIN ENDPOINT ANALYSIS')
    print('=' * 50)

    # Login as admin
    login_data = {
        'username': 'admin@bedrijfy.nl',
        'password': 'Admin123!'
    }

    response = requests.post(f'{BASE_URL}/auth/jwt/login', data=login_data)
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data['access_token']
        print('✅ Admin login successful')
        
        headers = {'Authorization': f'Bearer {access_token}'}
        
        # Test /tenants/my endpoint
        print('\nTesting /tenants/my endpoint:')
        response = requests.get(f'{BASE_URL}/tenants/my', headers=headers)
        print(f'Status: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            print(f'Tenant: {data.get("name")} (ID: {data.get("id")})')
        else:
            print(f'Response: {response.text}')
        
        # Test /users/me endpoint
        print('\nTesting /users/me endpoint:')
        response = requests.get(f'{BASE_URL}/users/me', headers=headers)
        print(f'Status: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            print(f'User: {data.get("email")} (Role: {data.get("role")})')
            print(f'Tenant ID: {data.get("tenant_id")}')
        
    else:
        print('❌ Admin login failed')

if __name__ == "__main__":
    test_system_owner_endpoints()
    test_admin_endpoints()
