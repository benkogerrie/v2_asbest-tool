#!/usr/bin/env python3
"""
Test script to debug the reports endpoint specifically.
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

def test_reports_endpoint_detailed(token):
    """Test reports endpoint with detailed debugging."""
    try:
        print(f"🔍 Testing reports endpoint with detailed debugging...")
        
        # Test with different query parameters
        test_cases = [
            "/reports",
            "/reports?page=1&page_size=10",
            "/reports?status=PROCESSING",
            "/reports?q=test"
        ]
        
        for endpoint in test_cases:
            print(f"\n   Testing: {endpoint}")
            
            response = requests.get(
                f"{API_BASE_URL}{endpoint}",
                headers={'Authorization': f'Bearer {token}'}
            )
            
            print(f"   Status: {response.status_code}")
            print(f"   Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Success: {len(data.get('items', []))} reports found")
                if data.get('items'):
                    print(f"   First report: {data['items'][0].get('id')}")
            else:
                print(f"   ❌ Error: {response.status_code}")
                print(f"   Response: {response.text}")
                
    except Exception as e:
        print(f"   ❌ Exception: {e}")

def test_other_endpoints_for_comparison(token):
    """Test other endpoints to see which ones work."""
    endpoints = [
        "/users/me",
        "/healthz",
        "/tenants",
        "/analyses/reports/test-id/analysis",
        "/findings/reports/test-id/findings"
    ]
    
    print(f"\n🔍 Testing other endpoints for comparison...")
    
    for endpoint in endpoints:
        try:
            response = requests.get(
                f"{API_BASE_URL}{endpoint}",
                headers={'Authorization': f'Bearer {token}'}
            )
            
            status_emoji = "✅" if response.status_code in [200, 201] else "❌"
            print(f"   {status_emoji} {endpoint}: {response.status_code}")
            
            if response.status_code not in [200, 201]:
                print(f"      Response: {response.text[:100]}...")
                
        except Exception as e:
            print(f"   ❌ {endpoint}: Exception - {e}")

def main():
    """Main function."""
    print("🔍 REPORTS ENDPOINT DEBUG")
    print("=" * 40)
    
    # Login
    token = login()
    if not token:
        return
    
    # Test reports endpoint
    print(f"\n1. Testing reports endpoint...")
    test_reports_endpoint_detailed(token)
    
    # Test other endpoints for comparison
    print(f"\n2. Testing other endpoints for comparison...")
    test_other_endpoints_for_comparison(token)
    
    print("\n📊 REPORTS DEBUG SUMMARY")
    print("=" * 40)
    print("This helps identify why reports endpoint fails")

if __name__ == "__main__":
    main()
