#!/usr/bin/env python3
"""
Test script to get exact error details.
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

def test_reports_with_verbose_logging(token):
    """Test reports endpoint with verbose logging."""
    try:
        print(f"🔍 Testing reports endpoint with verbose logging...")
        
        # Test with detailed headers
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'Test-Script/1.0',
            'X-Requested-With': 'XMLHttpRequest'
        }
        
        response = requests.get(
            f"{API_BASE_URL}/reports",
            headers=headers,
            timeout=30
        )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response Headers: {dict(response.headers)}")
        print(f"   Response Text: {response.text}")
        
        # Try to get more details
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

def test_tenants_with_verbose_logging(token):
    """Test tenants endpoint with verbose logging."""
    try:
        print(f"\n🔍 Testing tenants endpoint with verbose logging...")
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        response = requests.get(
            f"{API_BASE_URL}/tenants",
            headers=headers,
            timeout=30
        )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response Headers: {dict(response.headers)}")
        print(f"   Response Text: {response.text}")
        
        return response.status_code
        
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return None

def test_users_me_with_verbose_logging(token):
    """Test users/me endpoint with verbose logging for comparison."""
    try:
        print(f"\n🔍 Testing users/me endpoint with verbose logging...")
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        response = requests.get(
            f"{API_BASE_URL}/users/me",
            headers=headers,
            timeout=30
        )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response Headers: {dict(response.headers)}")
        print(f"   Response Text: {response.text}")
        
        return response.status_code
        
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return None

def main():
    """Main function."""
    print("🔍 EXACT ERROR TEST")
    print("=" * 30)
    
    # Login
    token = login()
    if not token:
        return
    
    # Test working endpoint first
    print(f"\n1. Testing working endpoint (/users/me)...")
    users_status = test_users_me_with_verbose_logging(token)
    
    # Test failing endpoints
    print(f"\n2. Testing failing endpoints...")
    reports_status = test_reports_with_verbose_logging(token)
    tenants_status = test_tenants_with_verbose_logging(token)
    
    # Summary
    print(f"\n📊 EXACT ERROR SUMMARY")
    print("=" * 30)
    print(f"/users/me: {users_status}")
    print(f"/reports: {reports_status}")
    print(f"/tenants: {tenants_status}")
    
    if users_status == 200 and reports_status == 401:
        print(f"\n🚨 ISSUE IDENTIFIED:")
        print(f"   - /users/me works (FastAPI Users basic functionality OK)")
        print(f"   - /reports fails with 401 (Custom dependency issue)")
        print(f"   - /tenants fails with 401 (Custom dependency issue)")
        print(f"   - Problem is in custom dependency functions")

if __name__ == "__main__":
    main()
