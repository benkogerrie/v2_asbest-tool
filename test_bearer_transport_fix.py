#!/usr/bin/env python3
"""
Test script to check if the BearerTransport fix resolves the issue.
"""
import requests
import json

# Railway API URL
API_BASE_URL = "https://v2asbest-tool-production.up.railway.app"

# Test credentials
TEST_EMAIL = "admin@bedrijfy.nl"
TEST_PASSWORD = "Admin123!"

def test_bearer_transport_fix():
    """Test if the BearerTransport fix resolves the issue."""
    try:
        print(f"🔍 Testing BearerTransport fix...")
        
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
        
        # Test the failing endpoints
        print(f"\n🔍 Testing failing endpoints...")
        
        failing_endpoints = [
            ("/reports", "Custom endpoint with get_current_active_user"),
            ("/tenants", "Custom endpoint with get_current_system_owner")
        ]
        
        for endpoint, description in failing_endpoints:
            try:
                response = requests.get(
                    f"{API_BASE_URL}{endpoint}",
                    headers={'Authorization': f'Bearer {token}'}
                )
                
                print(f"   {endpoint}: {response.status_code}")
                print(f"      {description}")
                
                if response.status_code == 401:
                    print(f"      ❌ 401 Unauthorized - Still failing")
                    try:
                        error_data = response.json()
                        print(f"      Error: {json.dumps(error_data, indent=6)}")
                    except:
                        print(f"      Raw error: {response.text}")
                elif response.status_code in [200, 201]:
                    print(f"      ✅ Success - Fixed!")
                else:
                    print(f"      ⚠️ Unexpected status: {response.status_code}")
                
            except Exception as e:
                print(f"   ❌ {endpoint}: Exception - {e}")
        
        # Test with system owner
        print(f"\n🔍 Testing with system owner...")
        
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
                print(f"      ❌ 401 Unauthorized - System owner still failing")
            elif response.status_code in [200, 201]:
                print(f"      ✅ Success - System owner works!")
        else:
            print(f"❌ System owner login failed: {system_response.status_code}")
        
    except Exception as e:
        print(f"❌ Exception: {e}")

def main():
    """Main function."""
    print("🔍 BEARER TRANSPORT FIX TEST")
    print("=" * 40)
    
    test_bearer_transport_fix()
    
    print(f"\n📊 BEARER TRANSPORT FIX SUMMARY")
    print("=" * 40)
    print("This test checks if the BearerTransport fix resolves the issue")

if __name__ == "__main__":
    main()
