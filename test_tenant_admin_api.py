#!/usr/bin/env python3
"""
Test script to debug tenant admin S. Jansen report visibility via API.
"""

import requests
import json

BASE_URL = 'https://v2asbest-tool-production.up.railway.app'

def test_tenant_admin_reports():
    """Test tenant admin S. Jansen report visibility via API."""
    
    print("🔍 Testing tenant admin S. Jansen report visibility...")
    
    # 1. Login as S. Jansen
    login_data = {
        "username": "s.jansen@bedrijf-y.nl",
        "password": "temp_password_123"
    }
    
    print(f"🔐 Logging in as {login_data['username']}...")
    
    try:
        response = requests.post(f"{BASE_URL}/auth/jwt/login", data=login_data)
        if response.status_code != 200:
            print(f"❌ Login failed: {response.status_code}")
            print(f"Response: {response.text}")
            return
        
        token_data = response.json()
        token = token_data.get('access_token')
        if not token:
            print("❌ No access token received")
            return
        
        print("✅ Login successful")
        
        # 2. Get user info
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/users/me", headers=headers)
        
        if response.status_code == 200:
            user_info = response.json()
            print(f"✅ User info:")
            print(f"   - Name: {user_info.get('first_name')} {user_info.get('last_name')}")
            print(f"   - Email: {user_info.get('email')}")
            print(f"   - Role: {user_info.get('role')}")
            print(f"   - Tenant ID: {user_info.get('tenant_id')}")
            print(f"   - Is Active: {user_info.get('is_active')}")
        else:
            print(f"❌ Failed to get user info: {response.status_code}")
            print(f"Response: {response.text}")
        
        # 3. Test reports endpoint
        print(f"\n📊 Testing /reports endpoint...")
        response = requests.get(f"{BASE_URL}/reports", headers=headers)
        
        if response.status_code == 200:
            reports_data = response.json()
            print(f"✅ Reports endpoint successful")
            print(f"   - Total reports: {reports_data.get('total', 0)}")
            print(f"   - Items in response: {len(reports_data.get('items', []))}")
            print(f"   - Page: {reports_data.get('page', 'N/A')}")
            print(f"   - Page size: {reports_data.get('page_size', 'N/A')}")
            
            # Show first few reports
            items = reports_data.get('items', [])
            if items:
                print(f"\n📋 First {min(3, len(items))} reports:")
                for i, report in enumerate(items[:3]):
                    print(f"   {i+1}. {report.get('filename', 'N/A')} (Status: {report.get('status', 'N/A')})")
            else:
                print("   No reports found")
                
        else:
            print(f"❌ Reports endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
        
        # 4. Test with different parameters
        print(f"\n🔍 Testing with different parameters...")
        
        # Test with page_size=100 to get all reports
        response = requests.get(f"{BASE_URL}/reports?page_size=100", headers=headers)
        if response.status_code == 200:
            reports_data = response.json()
            print(f"   - With page_size=100: {reports_data.get('total', 0)} total reports")
        
        # Test with status filter
        for status in ['PROCESSING', 'DONE', 'FAILED']:
            response = requests.get(f"{BASE_URL}/reports?status={status}", headers=headers)
            if response.status_code == 200:
                reports_data = response.json()
                count = reports_data.get('total', 0)
                print(f"   - Status {status}: {count} reports")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_tenant_admin_reports()
