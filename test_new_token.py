#!/usr/bin/env python3
"""
Test script to generate a new JWT token and test with it.
"""
import requests
import json

# Railway API URL
API_BASE_URL = "https://v2asbest-tool-production.up.railway.app"

# Test credentials
TEST_EMAIL = "admin@bedrijfy.nl"
TEST_PASSWORD = "Admin123!"

def login_and_test():
    """Login and test with fresh token."""
    try:
        print(f"🔍 Generating fresh JWT token...")
        
        # Login to get fresh token
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
            print(f"✅ Fresh login successful: {TEST_EMAIL}")
            print(f"   Token: {token[:50]}...")
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return
        
        # Test endpoints with fresh token
        print(f"\n🧪 Testing endpoints with fresh token...")
        
        endpoints = [
            ("/users/me", "FastAPI Users basic functionality"),
            ("/reports", "Custom dependency: get_current_active_user"),
            ("/tenants", "Custom dependency: get_current_system_owner"),
            ("/healthz", "No authentication required")
        ]
        
        for endpoint, description in endpoints:
            try:
                response = requests.get(
                    f"{API_BASE_URL}{endpoint}",
                    headers={'Authorization': f'Bearer {token}'}
                )
                
                status_emoji = "✅" if response.status_code in [200, 201] else "❌"
                print(f"   {status_emoji} {endpoint}: {response.status_code} - {description}")
                
                if response.status_code == 401:
                    print(f"      ❌ 401 Unauthorized - Still failing")
                elif response.status_code in [200, 201]:
                    print(f"      ✅ Success - Fixed!")
                
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
            system_data = system_response.json()
            system_token = system_data.get("access_token")
            print(f"✅ System owner login successful")
            
            # Test tenants endpoint with system owner
            response = requests.get(
                f"{API_BASE_URL}/tenants",
                headers={'Authorization': f'Bearer {system_token}'}
            )
            
            status_emoji = "✅" if response.status_code in [200, 201] else "❌"
            print(f"   {status_emoji} /tenants (system owner): {response.status_code}")
            
            if response.status_code == 401:
                print(f"      ❌ 401 Unauthorized - System owner also failing")
            elif response.status_code in [200, 201]:
                print(f"      ✅ Success - System owner works!")
        else:
            print(f"❌ System owner login failed: {system_response.status_code}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

def main():
    """Main function."""
    print("🔍 FRESH TOKEN TEST")
    print("=" * 30)
    
    login_and_test()
    
    print(f"\n📊 FRESH TOKEN SUMMARY")
    print("=" * 30)
    print("This test checks if the issue is related to cached JWT tokens")

if __name__ == "__main__":
    main()
