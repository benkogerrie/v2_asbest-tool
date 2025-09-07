#!/usr/bin/env python3
"""
Assign all reports to Admin Bedrijf Y tenant.
"""

import requests
import json

BASE_URL = 'https://v2asbest-tool-production.up.railway.app'

def assign_reports_to_tenant():
    """Assign all reports to Admin Bedrijf Y tenant."""
    
    print("🔍 ASSIGNING ALL REPORTS TO ADMIN BEDRIJF Y")
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
    
    # Get Admin Bedrijf Y user info to get tenant_id
    print("🔍 Getting Admin Bedrijf Y tenant ID...")
    response = requests.get(f"{BASE_URL}/users/", headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Failed to get users: {response.status_code}")
        return
    
    users = response.json()
    admin_tenant_id = None
    
    for user in users:
        if user.get('email') == 'admin@bedrijfy.nl':
            admin_tenant_id = user.get('tenant_id')
            print(f"✅ Found Admin Bedrijf Y tenant ID: {admin_tenant_id}")
            break
    
    if not admin_tenant_id:
        print("❌ Could not find Admin Bedrijf Y tenant ID")
        return
    
    # Get all reports
    print("\n🔍 Getting all reports...")
    response = requests.get(f"{BASE_URL}/reports/?page_size=100", headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Failed to get reports: {response.status_code}")
        return
    
    data = response.json()
    reports = data.get('items', [])
    total = data.get('total', 0)
    
    print(f"📊 Found {total} reports to assign")
    
    # Update each report
    updated_count = 0
    failed_count = 0
    
    for i, report in enumerate(reports, 1):
        report_id = report.get('id')
        filename = report.get('filename', 'Unknown')
        
        print(f"\n{i:2d}. Updating {filename}...")
        
        # Update report with tenant_id
        update_data = {
            "tenant_id": admin_tenant_id
        }
        
        response = requests.put(f"{BASE_URL}/reports/{report_id}", 
                              json=update_data, 
                              headers=headers)
        
        if response.status_code == 200:
            print(f"    ✅ Updated successfully")
            updated_count += 1
        else:
            print(f"    ❌ Failed: {response.status_code} - {response.text}")
            failed_count += 1
    
    print(f"\n🎉 ASSIGNMENT COMPLETE!")
    print(f"✅ Successfully updated: {updated_count} reports")
    print(f"❌ Failed to update: {failed_count} reports")
    print(f"📊 Total processed: {updated_count + failed_count} reports")
    
    # Test: Login as Admin Bedrijf Y and check reports
    print(f"\n🔍 Testing: Login as Admin Bedrijf Y...")
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
            print(f"✅ Admin Bedrijf Y can now see {admin_reports} reports")
        else:
            print(f"❌ Failed to get reports for Admin Bedrijf Y: {response.status_code}")
    else:
        print(f"❌ Failed to login as Admin Bedrijf Y: {response.status_code}")

if __name__ == "__main__":
    assign_reports_to_tenant()
