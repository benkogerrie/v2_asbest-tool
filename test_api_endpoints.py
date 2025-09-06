#!/usr/bin/env python3
"""
Test script to check individual API endpoints.
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

def test_endpoint(endpoint, token, method="GET", data=None):
    """Test individual endpoint."""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        headers = {'Authorization': f'Bearer {token}'}
        
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            headers['Content-Type'] = 'application/json'
            response = requests.post(url, headers=headers, json=data)
        
        print(f"🔍 {method} {endpoint}")
        print(f"   Status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            print(f"   ✅ Success")
            if response.headers.get('content-type', '').startswith('application/json'):
                try:
                    data = response.json()
                    if isinstance(data, dict) and len(data) < 5:
                        print(f"   Data: {data}")
                    else:
                        print(f"   Data: {type(data)} with {len(data) if hasattr(data, '__len__') else 'unknown'} items")
                except:
                    print(f"   Data: Non-JSON response")
        elif response.status_code in [404, 401, 422]:
            print(f"   ⚠️ Expected error: {response.status_code}")
        else:
            print(f"   ❌ Error: {response.status_code}")
            if response.text:
                print(f"   Response: {response.text[:200]}...")
        
        return response.status_code
        
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return None

def main():
    """Main function."""
    print("🔍 API ENDPOINTS TEST")
    print("=" * 40)
    
    # Login
    token = login()
    if not token:
        return
    
    # Test various endpoints
    endpoints_to_test = [
        ("/healthz", "GET"),
        ("/healthz/storage", "GET"),
        ("/reports", "GET"),
        ("/analyses/reports/test-id/analysis", "GET"),
        ("/findings/reports/test-id/findings", "GET"),
    ]
    
    print(f"\n🧪 Testing {len(endpoints_to_test)} endpoints...")
    
    results = {}
    for endpoint, method in endpoints_to_test:
        status = test_endpoint(endpoint, token, method)
        results[endpoint] = status
        print()
    
    # Summary
    print("📊 ENDPOINT TEST SUMMARY")
    print("=" * 40)
    
    working = [ep for ep, status in results.items() if status in [200, 201]]
    errors = [ep for ep, status in results.items() if status and status >= 500]
    expected_errors = [ep for ep, status in results.items() if status in [404, 401, 422]]
    
    print(f"✅ Working endpoints: {len(working)}")
    for ep in working:
        print(f"   - {ep}")
    
    print(f"⚠️ Expected errors: {len(expected_errors)}")
    for ep in expected_errors:
        print(f"   - {ep}")
    
    print(f"❌ Server errors: {len(errors)}")
    for ep in errors:
        print(f"   - {ep}")
    
    if errors:
        print(f"\n🔧 Issues found - these need investigation")
    else:
        print(f"\n🎯 All endpoints responding correctly")

if __name__ == "__main__":
    main()
