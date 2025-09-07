#!/usr/bin/env python3
"""
Check tenant assignment of reports.
"""

import requests
import json

BASE_URL = 'https://v2asbest-tool-production.up.railway.app'

def check_tenant_assignment():
    """Check tenant assignment of reports."""
    
    print("🔍 CHECKING TENANT ASSIGNMENT OF REPORTS")
    print("=" * 60)
    
    # Login as system owner
    response = requests.post(f"{BASE_URL}/auth/jwt/login", data={
        "username": "system@asbest-tool.nl",
        "password": "SystemOwner123!"
    })
    
    if response.status_code != 200:
        print(f"❌ System owner login failed: {response.status_code}")
        return
    
    token = response.json().get('access_token')
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get all reports
    response = requests.get(f"{BASE_URL}/reports/?page_size=100", headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Failed to get reports: {response.status_code}")
        return
    
    data = response.json()
    reports = data.get('items', [])
    
    print(f"📊 Total reports: {len(reports)}")
    print("=" * 60)
    
    # Check tenant assignment
    tenant_counts = {}
    null_tenant_count = 0
    
    for report in reports:
        tenant_name = report.get('tenant_name')
        if tenant_name is None:
            null_tenant_count += 1
        else:
            tenant_counts[tenant_name] = tenant_counts.get(tenant_name, 0) + 1
    
    print(f"📊 TENANT ASSIGNMENT SUMMARY:")
    print(f"   Reports with no tenant: {null_tenant_count}")
    for tenant, count in tenant_counts.items():
        print(f"   {tenant}: {count} reports")
    
    # Test different user logins
    print(f"\n🔍 TESTING DIFFERENT USER LOGINS:")
    print("=" * 40)
    
    # Test Admin Bedrijf Y
    print("1. Admin Bedrijf Y (admin@bedrijfy.nl):")
    response = requests.post(f"{BASE_URL}/auth/jwt/login", data={
        "username": "admin@bedrijfy.nl",
        "password": "Admin123!"
    })
    
    if response.status_code == 200:
        admin_token = response.json().get('access_token')
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = requests.get(f"{BASE_URL}/reports/", headers=admin_headers)
        if response.status_code == 200:
            data = response.json()
            admin_reports = data.get('total', 0)
            print(f"   ✅ Can see {admin_reports} reports")
        else:
            print(f"   ❌ Failed: {response.status_code}")
    else:
        print(f"   ❌ Login failed: {response.status_code}")
    
    # Test System Owner
    print("2. System Owner (system@asbest-tool.nl):")
    response = requests.post(f"{BASE_URL}/auth/jwt/login", data={
        "username": "system@asbest-tool.nl",
        "password": "SystemOwner123!"
    })
    
    if response.status_code == 200:
        system_token = response.json().get('access_token')
        system_headers = {"Authorization": f"Bearer {system_token}"}
        
        response = requests.get(f"{BASE_URL}/reports/", headers=system_headers)
        if response.status_code == 200:
            data = response.json()
            system_reports = data.get('total', 0)
            print(f"   ✅ Can see {system_reports} reports")
        else:
            print(f"   ❌ Failed: {response.status_code}")
    else:
        print(f"   ❌ Login failed: {response.status_code}")

if __name__ == "__main__":
    check_tenant_assignment()
