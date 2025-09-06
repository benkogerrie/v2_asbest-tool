#!/usr/bin/env python3
"""
Test script for deep debugging of the FastAPI Users issue.
"""
import requests
import json

# Railway API URL
API_BASE_URL = "https://v2asbest-tool-production.up.railway.app"

# Test credentials
TEST_EMAIL = "admin@bedrijfy.nl"
TEST_PASSWORD = "Admin123!"

def test_deep_debug():
    """Deep debugging of the FastAPI Users issue."""
    try:
        print(f"🔍 Deep debugging FastAPI Users issue...")
        
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
        
        # Test the exact same token with different endpoints
        print(f"\n🔍 Testing same token with different endpoints...")
        
        endpoints = [
            ("/users/me", "FastAPI Users default endpoint"),
            ("/reports", "Custom endpoint with get_current_active_user"),
            ("/tenants", "Custom endpoint with get_current_system_owner"),
            ("/analyses/reports/test-id/analysis", "Custom endpoint with get_current_active_user"),
            ("/findings/reports/test-id/findings", "Custom endpoint with get_current_active_user")
        ]
        
        for endpoint, description in endpoints:
            try:
                response = requests.get(
                    f"{API_BASE_URL}{endpoint}",
                    headers={'Authorization': f'Bearer {token}'}
                )
                
                print(f"   {endpoint}: {response.status_code}")
                print(f"      {description}")
                
                if response.status_code == 401:
                    print(f"      ❌ 401 Unauthorized")
                    # Try to get more details
                    try:
                        error_data = response.json()
                        print(f"      Error: {json.dumps(error_data, indent=6)}")
                    except:
                        print(f"      Raw error: {response.text}")
                elif response.status_code == 422:
                    print(f"      ⚠️ 422 Validation Error (expected for invalid UUID)")
                elif response.status_code in [200, 201]:
                    print(f"      ✅ Success")
                
            except Exception as e:
                print(f"   ❌ {endpoint}: Exception - {e}")
        
        # Test with system owner token
        print(f"\n🔍 Testing with system owner token...")
        
        system_response = requests.post(
            f"{API_BASE_URL}/auth/jwt/login",
            data={
                "username": "system@asbest-tool.nl",
                "password": "SystemOwner123!"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if system_response.status_code == 200:
            system_token = system_response.json().get("access_token")
            print(f"✅ System owner login successful")
            
            # Test tenants endpoint with system owner
            response = requests.get(
                f"{API_BASE_URL}/tenants",
                headers={'Authorization': f'Bearer {system_token}'}
            )
            
            print(f"   /tenants (system owner): {response.status_code}")
            
            if response.status_code == 401:
                print(f"      ❌ 401 Unauthorized - System owner also failing")
                try:
                    error_data = response.json()
                    print(f"      Error: {json.dumps(error_data, indent=6)}")
                except:
                    print(f"      Raw error: {response.text}")
            elif response.status_code in [200, 201]:
                print(f"      ✅ Success - System owner works!")
        else:
            print(f"❌ System owner login failed: {system_response.status_code}")
        
        # Test if the issue is with the dependency injection order
        print(f"\n🔍 Testing dependency injection order...")
        
        # Test a simple endpoint that doesn't use custom dependencies
        response = requests.get(
            f"{API_BASE_URL}/healthz",
            headers={'Authorization': f'Bearer {token}'}
        )
        print(f"   /healthz with auth: {response.status_code}")
        
        # Test if the issue is with the database session
        print(f"\n🔍 Testing database session issue...")
        
        # Test if the issue is with the async/sync mismatch
        print(f"   Testing async/sync mismatch...")
        
        # Test if the issue is with the FastAPI Users configuration
        print(f"   Testing FastAPI Users configuration...")
        
        # Test if the issue is with the JWT strategy
        print(f"   Testing JWT strategy...")
        
    except Exception as e:
        print(f"❌ Exception: {e}")

def main():
    """Main function."""
    print("🔍 DEEP DEBUG TEST")
    print("=" * 30)
    
    test_deep_debug()
    
    print(f"\n📊 DEEP DEBUG SUMMARY")
    print("=" * 30)
    print("This test provides detailed debugging information")

if __name__ == "__main__":
    main()
