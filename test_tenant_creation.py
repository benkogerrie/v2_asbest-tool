#!/usr/bin/env python3
"""
Test tenant creation functionality
"""
import requests
import json

BASE_URL = 'https://v2asbest-tool-production.up.railway.app'

def test_tenant_creation():
    """Test if system owner can create tenants via API"""
    print('🔍 TESTING TENANT CREATION VIA API')
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
        
        # Test tenant creation
        tenant_data = {
            'name': 'Test Bedrijf Z',
            'kvk': '99999999',
            'contact_email': 'info@bedrijf-z.nl'
        }
        
        print('\nTesting POST /tenants/ endpoint:')
        response = requests.post(f'{BASE_URL}/tenants/', headers=headers, json=tenant_data)
        print(f'Status: {response.status_code}')
        print(f'Response: {response.text}')
        
        if response.status_code == 201:
            print('✅ Tenant creation successful!')
            created_tenant = response.json()
            print(f'Created tenant: {created_tenant.get("name")} (ID: {created_tenant.get("id")})')
        else:
            print('❌ Tenant creation failed')
            
    else:
        print('❌ Login failed')

def test_ui_functionality():
    """Test if UI can load tenants"""
    print('\n🔍 TESTING UI FUNCTIONALITY')
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
        
        # Test GET /tenants/ (what UI calls)
        print('\nTesting GET /tenants/ (UI call):')
        response = requests.get(f'{BASE_URL}/tenants/', headers=headers)
        print(f'Status: {response.status_code}')
        
        if response.status_code == 200:
            tenants = response.json()
            print(f'✅ Found {len(tenants)} tenants')
            for tenant in tenants:
                print(f'  - {tenant.get("name")} (KvK: {tenant.get("kvk")})')
        else:
            print('❌ Failed to load tenants')
            print(f'Response: {response.text}')
            
    else:
        print('❌ Login failed')

if __name__ == "__main__":
    test_tenant_creation()
    test_ui_functionality()
