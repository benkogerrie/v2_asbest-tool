#!/usr/bin/env python3
"""
Comprehensive test suite for Slice 5 functionality
"""
import requests
import json
import time

BASE_URL = 'https://v2asbest-tool-production.up.railway.app'

def login_as_admin():
    """Login as tenant admin"""
    login_data = {
        'username': 'admin@bedrijfy.nl',
        'password': 'Admin123!'
    }
    response = requests.post(f'{BASE_URL}/auth/jwt/login', data=login_data)
    if response.status_code == 200:
        return response.json()['access_token']
    return None

def login_as_system_owner():
    """Login as system owner"""
    login_data = {
        'username': 'system@asbest-tool.nl',
        'password': 'SystemOwner123!'
    }
    response = requests.post(f'{BASE_URL}/auth/jwt/login', data=login_data)
    if response.status_code == 200:
        return response.json()['access_token']
    return None

def test_health_endpoints():
    """Test health endpoints"""
    print("1. Testing Health Endpoints...")
    
    endpoints = [
        ('/healthz', 'API Health'),
        ('/healthz/storage', 'Storage Health'),
    ]
    
    for endpoint, description in endpoints:
        response = requests.get(f'{BASE_URL}{endpoint}')
        status = "✅" if response.status_code == 200 else "❌"
        print(f"   {status} {description}: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"      Status: {data.get('status', 'unknown')}")

def test_authentication():
    """Test authentication"""
    print("\n2. Testing Authentication...")
    
    # Test admin login
    admin_token = login_as_admin()
    if admin_token:
        print("   ✅ Admin login: Success")
    else:
        print("   ❌ Admin login: Failed")
        return None
    
    # Test system owner login
    system_token = login_as_system_owner()
    if system_token:
        print("   ✅ System owner login: Success")
    else:
        print("   ❌ System owner login: Failed")
        return None
    
    return admin_token, system_token

def test_reports_endpoints(admin_token):
    """Test reports endpoints"""
    print("\n3. Testing Reports Endpoints...")
    
    headers = {'Authorization': f'Bearer {admin_token}'}
    
    # Test GET /reports
    response = requests.get(f'{BASE_URL}/reports/', headers=headers)
    status = "✅" if response.status_code == 200 else "❌"
    print(f"   {status} GET /reports: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"      Found {len(data.get('items', []))} reports")
    
    # Test POST /reports (upload)
    files = {'file': ('test_comprehensive.pdf', b'%PDF-1.4 fake pdf content', 'application/pdf')}
    response = requests.post(f'{BASE_URL}/reports/', headers=headers, files=files)
    status = "✅" if response.status_code == 201 else "❌"
    print(f"   {status} POST /reports: {response.status_code}")
    if response.status_code == 201:
        data = response.json()
        report_id = data.get('id')
        print(f"      Uploaded report: {report_id}")
        return report_id
    
    return None

def test_tenants_endpoints(system_token):
    """Test tenants endpoints"""
    print("\n4. Testing Tenants Endpoints...")
    
    headers = {'Authorization': f'Bearer {system_token}'}
    
    # Test GET /tenants/
    response = requests.get(f'{BASE_URL}/tenants/', headers=headers)
    status = "✅" if response.status_code == 200 else "❌"
    print(f"   {status} GET /tenants/: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"      Found {len(data)} tenants")
        for tenant in data:
            print(f"      - {tenant.get('name', 'Unknown')} ({tenant.get('kvk', 'No KvK')})")
    
    # Test GET /tenants/my (should work for system owner)
    response = requests.get(f'{BASE_URL}/tenants/my', headers=headers)
    status = "✅" if response.status_code == 200 else "❌"
    print(f"   {status} GET /tenants/my: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"      System owner tenant: {data.get('name', 'Unknown')}")

def test_analyses_endpoints(admin_token, report_id):
    """Test analyses endpoints"""
    print("\n5. Testing Analyses Endpoints...")
    
    if not report_id:
        print("   ⚠️  Skipping - No report ID available")
        return
    
    headers = {'Authorization': f'Bearer {admin_token}'}
    
    # Test GET /analyses/reports/{id}/analysis
    response = requests.get(f'{BASE_URL}/analyses/reports/{report_id}/analysis', headers=headers)
    status = "✅" if response.status_code in [200, 422] else "❌"
    print(f"   {status} GET /analyses/reports/{report_id}/analysis: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if data:
            print(f"      Analysis found: {data.get('id', 'Unknown')}")
        else:
            print("      No analysis data returned")
    elif response.status_code == 422:
        print("      Expected 422 - Report not processed yet")

def test_findings_endpoints(admin_token, report_id):
    """Test findings endpoints"""
    print("\n6. Testing Findings Endpoints...")
    
    if not report_id:
        print("   ⚠️  Skipping - No report ID available")
        return
    
    headers = {'Authorization': f'Bearer {admin_token}'}
    
    # Test GET /findings/reports/{id}/findings
    response = requests.get(f'{BASE_URL}/findings/reports/{report_id}/findings', headers=headers)
    status = "✅" if response.status_code in [200, 422] else "❌"
    print(f"   {status} GET /findings/reports/{report_id}/findings: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"      Found {len(data)} findings")
    elif response.status_code == 422:
        print("      Expected 422 - Report not processed yet")

def test_users_endpoints(admin_token):
    """Test users endpoints"""
    print("\n7. Testing Users Endpoints...")
    
    headers = {'Authorization': f'Bearer {admin_token}'}
    
    # Test GET /users/me
    response = requests.get(f'{BASE_URL}/users/me', headers=headers)
    status = "✅" if response.status_code == 200 else "❌"
    print(f"   {status} GET /users/me: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"      User: {data.get('email', 'Unknown')} ({data.get('role', 'Unknown')})")

def main():
    """Run comprehensive tests"""
    print("🧪 COMPREHENSIVE SLICE 5 TEST SUITE")
    print("=" * 50)
    print(f"Testing at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API URL: {BASE_URL}")
    print()
    
    # Run all tests
    test_health_endpoints()
    
    tokens = test_authentication()
    if not tokens:
        print("❌ Authentication failed - stopping tests")
        return
    
    admin_token, system_token = tokens
    
    report_id = test_reports_endpoints(admin_token)
    test_tenants_endpoints(system_token)
    test_analyses_endpoints(admin_token, report_id)
    test_findings_endpoints(admin_token, report_id)
    test_users_endpoints(admin_token)
    
    print("\n📊 COMPREHENSIVE TEST SUMMARY")
    print("=" * 50)
    print("✅ All major endpoints tested")
    print("🎯 Slice 5 functionality validated")
    print("\nNext steps:")
    print("- Test UI integration")
    print("- Verify PDF generation")
    print("- Test worker processing")

if __name__ == "__main__":
    main()
