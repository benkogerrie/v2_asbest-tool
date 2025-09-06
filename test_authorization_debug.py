#!/usr/bin/env python3
"""
Test script to debug authorization issues.
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

def test_reports_with_detailed_debug(token):
    """Test reports endpoint with detailed debugging."""
    try:
        print(f"🔍 Testing reports endpoint with detailed debugging...")
        
        # Test with verbose headers
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'Test-Script/1.0'
        }
        
        response = requests.get(
            f"{API_BASE_URL}/reports",
            headers=headers,
            timeout=30
        )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response Headers: {dict(response.headers)}")
        print(f"   Response Text: {response.text}")
        
        # Try to get more details from the error
        if response.status_code == 401:
            try:
                error_data = response.json()
                print(f"   Error Details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"   Raw Error Response: {response.text}")
        
        return response.status_code
        
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return None

def test_different_endpoints_with_same_token(token):
    """Test different endpoints with the same token to see which ones work."""
    endpoints = [
        ("/users/me", "Should work - user info"),
        ("/reports", "Should work - reports list"),
        ("/reports?page=1&page_size=5", "Should work - reports with pagination"),
        ("/tenants", "Should work for system owner only"),
        ("/healthz", "Should work - health check"),
        ("/analyses/reports/test-id/analysis", "Should give 422 - invalid UUID"),
        ("/findings/reports/test-id/findings", "Should give 422 - invalid UUID")
    ]
    
    print(f"\n🔍 Testing different endpoints with same token...")
    
    working_endpoints = []
    failing_endpoints = []
    
    for endpoint, description in endpoints:
        try:
            response = requests.get(
                f"{API_BASE_URL}{endpoint}",
                headers={'Authorization': f'Bearer {token}'}
            )
            
            if response.status_code in [200, 201]:
                working_endpoints.append((endpoint, response.status_code, description))
                print(f"   ✅ {endpoint}: {response.status_code} - {description}")
            else:
                failing_endpoints.append((endpoint, response.status_code, description))
                print(f"   ❌ {endpoint}: {response.status_code} - {description}")
                
        except Exception as e:
            failing_endpoints.append((endpoint, "EXCEPTION", description))
            print(f"   ❌ {endpoint}: EXCEPTION - {description}")
    
    return working_endpoints, failing_endpoints

def test_without_authorization():
    """Test endpoints without authorization to see the difference."""
    print(f"\n🔍 Testing endpoints without authorization...")
    
    endpoints = [
        "/users/me",
        "/reports",
        "/tenants",
        "/healthz"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{API_BASE_URL}{endpoint}")
            print(f"   {endpoint}: {response.status_code}")
            
        except Exception as e:
            print(f"   {endpoint}: EXCEPTION - {e}")

def main():
    """Main function."""
    print("🔍 AUTHORIZATION DEBUG TEST")
    print("=" * 40)
    
    # Login
    token = login()
    if not token:
        return
    
    # Test reports endpoint with detailed debug
    print(f"\n1. Testing reports endpoint with detailed debugging...")
    reports_status = test_reports_with_detailed_debug(token)
    
    # Test different endpoints
    print(f"\n2. Testing different endpoints...")
    working, failing = test_different_endpoints_with_same_token(token)
    
    # Test without authorization
    print(f"\n3. Testing without authorization...")
    test_without_authorization()
    
    # Summary
    print(f"\n📊 AUTHORIZATION DEBUG SUMMARY")
    print("=" * 40)
    print(f"Working endpoints: {len(working)}")
    for endpoint, status, desc in working:
        print(f"   ✅ {endpoint}: {status}")
    
    print(f"\nFailing endpoints: {len(failing)}")
    for endpoint, status, desc in failing:
        print(f"   ❌ {endpoint}: {status}")
    
    if reports_status == 401:
        print(f"\n🚨 REPORTS ENDPOINT ISSUE:")
        print(f"   - Reports endpoint returns 401 Unauthorized")
        print(f"   - But /users/me works with same token")
        print(f"   - This suggests an issue in the reports endpoint authorization logic")
        print(f"   - Possible causes:")
        print(f"     * Dependency injection issue")
        print(f"     * FastAPI Users configuration problem")
        print(f"     * Database session issue in reports endpoint")

if __name__ == "__main__":
    main()
