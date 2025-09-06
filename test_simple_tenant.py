#!/usr/bin/env python3
"""
Test simple tenant + admin creation
"""
import requests
import json

BASE_URL = 'https://v2asbest-tool-production.up.railway.app'

def test_simple_tenant_creation():
    """Test with minimal data"""
    print('🔍 TESTING SIMPLE TENANT + ADMIN CREATION')
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
        
        # Test with minimal data
        simple_data = {
            'tenant': {
                'name': 'Simple Test',
                'kvk': '55555555',
                'contact_email': 'simple@test.nl'
            },
            'admin': {
                'first_name': 'Simple',
                'last_name': 'Admin',
                'email': 'admin@simple.nl',
                'role': 'ADMIN'
            }
        }
        
        print('\nTesting with minimal data:')
        response = requests.post(f'{BASE_URL}/tenants/with-admin', headers=headers, json=simple_data)
        print(f'Status: {response.status_code}')
        
        if response.status_code == 201:
            result = response.json()
            print('✅ SUCCESS!')
            print(f'Tenant: {result["tenant"]["name"]}')
            print(f'Admin: {result["admin"]["email"]}')
            print(f'Password: {result["temp_password"]}')
        else:
            print(f'❌ Error: {response.status_code}')
            print(f'Response: {response.text[:300]}')
            
    else:
        print('❌ Login failed')

if __name__ == "__main__":
    test_simple_tenant_creation()
