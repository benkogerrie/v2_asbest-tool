#!/usr/bin/env python3
"""
Test script to demonstrate the FastAPI Users authorization problem.
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

def test_endpoints(token):
    """Test various endpoints to demonstrate the problem."""
    print(f"🔍 Testing endpoints to demonstrate the problem...")
    
    endpoints = [
        ("/users/me", "FastAPI Users basic functionality", "Should work"),
        ("/reports", "Custom dependency: get_current_active_user", "Should work but fails"),
        ("/tenants", "Custom dependency: get_current_system_owner", "Should work but fails"),
        ("/healthz", "No authentication required", "Should work"),
        ("/analyses/reports/test-id/analysis", "Custom dependency: get_current_active_user", "Should give 422 (invalid UUID)"),
        ("/findings/reports/test-id/findings", "Custom dependency: get_current_active_user", "Should give 422 (invalid UUID)")
    ]
    
    results = []
    
    for endpoint, description, expected in endpoints:
        try:
            response = requests.get(
                f"{API_BASE_URL}{endpoint}",
                headers={'Authorization': f'Bearer {token}'}
            )
            
            status_emoji = "✅" if response.status_code in [200, 201] else "❌"
            print(f"   {status_emoji} {endpoint}: {response.status_code}")
            print(f"      Description: {description}")
            print(f"      Expected: {expected}")
            
            if response.status_code == 401:
                print(f"      ❌ 401 Unauthorized - FastAPI Users dependency issue")
            elif response.status_code == 422:
                print(f"      ⚠️ 422 Validation Error - Expected for invalid UUID")
            elif response.status_code in [200, 201]:
                print(f"      ✅ Success")
            
            results.append({
                "endpoint": endpoint,
                "status": response.status_code,
                "description": description,
                "expected": expected
            })
            
        except Exception as e:
            print(f"   ❌ {endpoint}: Exception - {e}")
            results.append({
                "endpoint": endpoint,
                "status": "EXCEPTION",
                "description": description,
                "expected": expected
            })
    
    return results

def get_user_info(token):
    """Get user information to show the user exists and is valid."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/users/me",
            headers={'Authorization': f'Bearer {token}'}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n👤 User Information:")
            print(f"   ID: {data.get('id')}")
            print(f"   Email: {data.get('email')}")
            print(f"   Role: {data.get('role')}")
            print(f"   Tenant ID: {data.get('tenant_id')}")
            print(f"   Is Active: {data.get('is_active')}")
            print(f"   Is Verified: {data.get('is_verified')}")
            return data
        else:
            print(f"❌ Failed to get user info: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Exception getting user info: {e}")
        return None

def main():
    """Main function to demonstrate the problem."""
    print("🔍 FASTAPI USERS AUTHORIZATION PROBLEM DEMONSTRATION")
    print("=" * 60)
    
    # Login
    token = login()
    if not token:
        return
    
    # Get user info
    user_info = get_user_info(token)
    
    # Test endpoints
    print(f"\n🧪 Testing endpoints...")
    results = test_endpoints(token)
    
    # Summary
    print(f"\n📊 PROBLEM SUMMARY")
    print("=" * 60)
    
    working = [r for r in results if r["status"] in [200, 201]]
    failing = [r for r in results if r["status"] == 401]
    expected_errors = [r for r in results if r["status"] == 422]
    
    print(f"✅ Working endpoints: {len(working)}")
    for r in working:
        print(f"   - {r['endpoint']}: {r['status']}")
    
    print(f"\n❌ Failing endpoints (401 Unauthorized): {len(failing)}")
    for r in failing:
        print(f"   - {r['endpoint']}: {r['status']} - {r['description']}")
    
    print(f"\n⚠️ Expected errors (422 Validation): {len(expected_errors)}")
    for r in expected_errors:
        print(f"   - {r['endpoint']}: {r['status']} - {r['description']}")
    
    print(f"\n🚨 PROBLEM IDENTIFIED:")
    print(f"   - FastAPI Users basic functionality works (/users/me)")
    print(f"   - Custom dependency functions fail (get_current_active_user, get_current_system_owner)")
    print(f"   - JWT token validation works")
    print(f"   - Users exist in database and are valid")
    print(f"   - Issue is in FastAPI Users dependency injection configuration")

if __name__ == "__main__":
    main()
