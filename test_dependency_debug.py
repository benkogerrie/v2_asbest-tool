#!/usr/bin/env python3
"""
Test script to debug the dependency injection issue.
"""
import requests
import json

# Railway API URL
API_BASE_URL = "https://v2asbest-tool-production.up.railway.app"

# Test credentials
TEST_EMAIL = "admin@bedrijfy.nl"
TEST_PASSWORD = "Admin123!"

def test_dependency_chain():
    """Test the dependency chain to see where it breaks."""
    try:
        print(f"🔍 Testing dependency chain...")
        
        # Login
        response = requests.post(
            f"{API_BASE_URL}/auth/jwt/login",
            data={
                "username": TEST_EMAIL,
                "password": TEST_PASSWORD
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code != 200:
            print(f"❌ Login failed: {response.status_code}")
            return
        
        token = response.json().get("access_token")
        print(f"✅ Login successful")
        
        # Test different endpoints to see the pattern
        endpoints = [
            ("/users/me", "FastAPI Users default endpoint"),
            ("/reports", "Custom endpoint with get_current_active_user"),
            ("/tenants", "Custom endpoint with get_current_system_owner"),
            ("/analyses/reports/test-id/analysis", "Custom endpoint with get_current_active_user"),
            ("/findings/reports/test-id/findings", "Custom endpoint with get_current_active_user")
        ]
        
        print(f"\n🧪 Testing dependency chain...")
        
        for endpoint, description in endpoints:
            try:
                response = requests.get(
                    f"{API_BASE_URL}{endpoint}",
                    headers={'Authorization': f'Bearer {token}'}
                )
                
                status_emoji = "✅" if response.status_code in [200, 201] else "❌"
                print(f"   {status_emoji} {endpoint}: {response.status_code}")
                print(f"      {description}")
                
                if response.status_code == 401:
                    print(f"      ❌ 401 Unauthorized - Dependency injection failed")
                elif response.status_code == 422:
                    print(f"      ⚠️ 422 Validation Error - Expected for invalid UUID")
                elif response.status_code in [200, 201]:
                    print(f"      ✅ Success - Dependency injection working")
                
            except Exception as e:
                print(f"   ❌ {endpoint}: Exception - {e}")
        
        # Test with different HTTP methods
        print(f"\n🔍 Testing different HTTP methods...")
        
        methods = ["GET", "POST", "PUT", "DELETE"]
        for method in methods:
            try:
                if method == "GET":
                    response = requests.get(
                        f"{API_BASE_URL}/reports",
                        headers={'Authorization': f'Bearer {token}'}
                    )
                elif method == "POST":
                    response = requests.post(
                        f"{API_BASE_URL}/reports",
                        headers={'Authorization': f'Bearer {token}'}
                    )
                elif method == "PUT":
                    response = requests.put(
                        f"{API_BASE_URL}/reports",
                        headers={'Authorization': f'Bearer {token}'}
                    )
                elif method == "DELETE":
                    response = requests.delete(
                        f"{API_BASE_URL}/reports",
                        headers={'Authorization': f'Bearer {token}'}
                    )
                
                print(f"   {method} /reports: {response.status_code}")
                
            except Exception as e:
                print(f"   {method} /reports: Exception - {e}")
        
    except Exception as e:
        print(f"❌ Exception: {e}")

def main():
    """Main function."""
    print("🔍 DEPENDENCY CHAIN DEBUG")
    print("=" * 40)
    
    test_dependency_chain()
    
    print(f"\n📊 DEPENDENCY CHAIN SUMMARY")
    print("=" * 40)
    print("This test helps identify where the dependency chain breaks")

if __name__ == "__main__":
    main()
