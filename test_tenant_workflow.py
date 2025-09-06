#!/usr/bin/env python3
"""
Test the new tenant + admin workflow
"""
import requests
import json

BASE_URL = 'https://v2asbest-tool-production.up.railway.app'

def test_tenant_with_admin_creation():
    """Test the new tenant + admin creation endpoint"""
    print('🔍 TESTING TENANT + ADMIN WORKFLOW')
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
        
        # Test tenant + admin creation
        tenant_admin_data = {
            "tenant": {
                "name": "Test Bedrijf Workflow",
                "kvk": "88888888",
                "contact_email": "info@workflow-test.nl",
                "phone": "+31 20 888 8888",
                "address": "Workflow Straat 123, 1000 AB Amsterdam",
                "website": "https://www.workflow-test.nl",
                "industry": "Software Development"
            },
            "admin": {
                "first_name": "Workflow",
                "last_name": "Admin",
                "email": "admin@workflow-test.nl",
                "phone": "+31 6 888 88888",
                "job_title": "IT Manager",
                "department": "IT",
                "role": "ADMIN"
            }
        }
        
        print('\nTesting POST /tenants/with-admin endpoint:')
        response = requests.post(f'{BASE_URL}/tenants/with-admin', headers=headers, json=tenant_admin_data)
        print(f'Status: {response.status_code}')
        
        if response.status_code == 201:
            result = response.json()
            print('✅ Tenant + Admin creation successful!')
            print(f'Tenant: {result["tenant"]["name"]} (ID: {result["tenant"]["id"]})')
            print(f'Admin: {result["admin"]["first_name"]} {result["admin"]["last_name"]} ({result["admin"]["email"]})')
            print(f'Temporary password: {result["temp_password"]}')
            print(f'Invitation sent: {result["invitation_sent"]}')
        else:
            print('❌ Tenant + Admin creation failed')
            print(f'Response: {response.text}')
            
    else:
        print('❌ Login failed')

def test_extended_tenant_fields():
    """Test if extended tenant fields are working"""
    print('\n🔍 TESTING EXTENDED TENANT FIELDS')
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
        
        # Test GET /tenants/ to see if extended fields are returned
        print('\nTesting GET /tenants/ with extended fields:')
        response = requests.get(f'{BASE_URL}/tenants/', headers=headers)
        print(f'Status: {response.status_code}')
        
        if response.status_code == 200:
            tenants = response.json()
            print(f'✅ Found {len(tenants)} tenants')
            for tenant in tenants:
                print(f'  - {tenant.get("name")}')
                print(f'    Address: {tenant.get("address", "Not set")}')
                print(f'    Phone: {tenant.get("phone", "Not set")}')
                print(f'    Website: {tenant.get("website", "Not set")}')
                print(f'    Industry: {tenant.get("industry", "Not set")}')
        else:
            print('❌ Failed to load tenants')
            print(f'Response: {response.text}')
            
    else:
        print('❌ Login failed')

if __name__ == "__main__":
    test_tenant_with_admin_creation()
    test_extended_tenant_fields()
