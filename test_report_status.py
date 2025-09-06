#!/usr/bin/env python3
"""
Test script to debug report status endpoint.
"""
import requests
import json

# Railway API URL
API_BASE_URL = "https://v2asbest-tool-production.up.railway.app"

# Test credentials
TEST_EMAIL = "admin@bedrijfy.nl"
TEST_PASSWORD = "Admin123!"

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

def test_report_status(report_id, token):
    """Test report status endpoint with detailed error info."""
    try:
        print(f"🔍 Testing report status for: {report_id}")
        
        response = requests.get(
            f"{API_BASE_URL}/reports/{report_id}",
            headers={'Authorization': f'Bearer {token}'}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Report data: {json.dumps(data, indent=2)}")
            return data
        else:
            print(f"❌ Error Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Request error: {e}")
        return None

def test_reports_list(token):
    """Test reports list endpoint."""
    try:
        print(f"🔍 Testing reports list endpoint")
        
        response = requests.get(
            f"{API_BASE_URL}/reports",
            headers={'Authorization': f'Bearer {token}'}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Reports list: {len(data.get('items', []))} reports found")
            if data.get('items'):
                first_report = data['items'][0]
                print(f"First report: {first_report.get('id')} - {first_report.get('filename')}")
                return first_report.get('id')
            return None
        else:
            print(f"❌ Error Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Request error: {e}")
        return None

def main():
    """Main function."""
    print("🔍 REPORT STATUS DEBUG TEST")
    print("=" * 40)
    
    # Login
    token = login()
    if not token:
        return
    
    # Test reports list first
    print("\n1. Testing reports list...")
    report_id = test_reports_list(token)
    
    if report_id:
        print(f"\n2. Testing report status for {report_id}...")
        test_report_status(report_id, token)
    else:
        print("\n2. No reports found to test status endpoint")
    
    print("\n📊 DEBUG SUMMARY")
    print("=" * 40)
    print("This test helps identify the exact cause of 500 errors")

if __name__ == "__main__":
    main()
