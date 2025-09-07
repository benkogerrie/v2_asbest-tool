#!/usr/bin/env python3
"""
Test script with correct credentials from seed script.
"""

import requests
import json

BASE_URL = 'https://v2asbest-tool-production.up.railway.app'

def test_with_correct_credentials():
    """Test with correct credentials from seed script."""
    
    print("🔍 Testing with correct credentials from seed script...")
    
    # Correct credentials from seed script
    credentials = [
        {
            "name": "System Owner",
            "username": "system@asbest-tool.nl",
            "password": "SystemOwner123!",
            "expected_role": "SYSTEM_OWNER"
        },
        {
            "name": "Tenant Admin",
            "username": "admin@bedrijfy.nl", 
            "password": "Admin123!",
            "expected_role": "ADMIN"
        }
    ]
    
    for cred in credentials:
        print(f"\n🔐 Testing {cred['name']}...")
        
        try:
            response = requests.post(f"{BASE_URL}/auth/jwt/login", data={
                "username": cred['username'],
                "password": cred['password']
            })
            
            if response.status_code == 200:
                print(f"✅ Login successful for {cred['name']}")
                token_data = response.json()
                token = token_data.get('access_token')
                
                # Get user info
                headers = {"Authorization": f"Bearer {token}"}
                response = requests.get(f"{BASE_URL}/users/me", headers=headers)
                
                if response.status_code == 200:
                    user_info = response.json()
                    print(f"   - Name: {user_info.get('first_name')} {user_info.get('last_name')}")
                    print(f"   - Email: {user_info.get('email')}")
                    print(f"   - Role: {user_info.get('role')} (expected: {cred['expected_role']})")
                    print(f"   - Tenant ID: {user_info.get('tenant_id')}")
                    print(f"   - Is Active: {user_info.get('is_active')}")
                    
                    # Test reports endpoint
                    response = requests.get(f"{BASE_URL}/reports", headers=headers)
                    if response.status_code == 200:
                        reports_data = response.json()
                        print(f"   - Reports visible: {reports_data.get('total', 0)}")
                        
                        # Show first few reports
                        items = reports_data.get('items', [])
                        if items:
                            print(f"   - First {min(3, len(items))} reports:")
                            for i, report in enumerate(items[:3]):
                                print(f"     {i+1}. {report.get('filename', 'N/A')} (Status: {report.get('status', 'N/A')})")
                        else:
                            print("   - No reports found")
                    else:
                        print(f"   - Reports endpoint failed: {response.status_code}")
                        print(f"   - Response: {response.text}")
                
            else:
                print(f"❌ Login failed for {cred['name']}: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error testing {cred['name']}: {e}")

if __name__ == "__main__":
    test_with_correct_credentials()
