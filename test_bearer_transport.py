#!/usr/bin/env python3
"""
Test script to check if the issue is with BearerTransport.
"""
import requests
import json

# Railway API URL
API_BASE_URL = "https://v2asbest-tool-production.up.railway.app"

# Test credentials
TEST_EMAIL = "admin@bedrijfy.nl"
TEST_PASSWORD = "Admin123!"

def test_bearer_transport_issue():
    """Test if the issue is with BearerTransport."""
    try:
        print(f"🔍 Testing BearerTransport issue...")
        
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
        print(f"   Token: {token[:50]}...")
        
        # Test different authorization header formats
        print(f"\n🔍 Testing different authorization header formats...")
        
        header_formats = [
            ("Bearer", f"Bearer {token}"),
            ("bearer", f"bearer {token}"),
            ("BEARER", f"BEARER {token}"),
            ("Authorization", f"Authorization: Bearer {token}"),
            ("Token", f"Token {token}"),
            ("token", f"token {token}"),
        ]
        
        for header_name, header_value in header_formats:
            try:
                response = requests.get(
                    f"{API_BASE_URL}/users/me",
                    headers={header_name: header_value}
                )
                
                status_emoji = "✅" if response.status_code == 200 else "❌"
                print(f"   {status_emoji} {header_name}: {response.status_code}")
                
            except Exception as e:
                print(f"   ❌ {header_name}: Exception - {e}")
        
        # Test with different header combinations
        print(f"\n🔍 Testing with different header combinations...")
        
        combinations = [
            {"Authorization": f"Bearer {token}"},
            {"Authorization": f"bearer {token}"},
            {"Authorization": f"BEARER {token}"},
            {"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            {"Authorization": f"Bearer {token}", "Accept": "application/json"},
            {"Authorization": f"Bearer {token}", "User-Agent": "Test-Script/1.0"},
        ]
        
        for headers in combinations:
            try:
                response = requests.get(
                    f"{API_BASE_URL}/users/me",
                    headers=headers
                )
                
                status_emoji = "✅" if response.status_code == 200 else "❌"
                header_str = ", ".join([f"{k}: {v[:20]}..." for k, v in headers.items()])
                print(f"   {status_emoji} {header_str}: {response.status_code}")
                
            except Exception as e:
                print(f"   ❌ {header_str}: Exception - {e}")
        
        # Test the failing endpoints with the working header format
        print(f"\n🔍 Testing failing endpoints with working header format...")
        
        failing_endpoints = [
            "/reports",
            "/tenants"
        ]
        
        for endpoint in failing_endpoints:
            try:
                response = requests.get(
                    f"{API_BASE_URL}{endpoint}",
                    headers={"Authorization": f"Bearer {token}"}
                )
                
                status_emoji = "✅" if response.status_code in [200, 201] else "❌"
                print(f"   {status_emoji} {endpoint}: {response.status_code}")
                
                if response.status_code == 401:
                    print(f"      ❌ Still failing with 401")
                elif response.status_code in [200, 201]:
                    print(f"      ✅ Fixed!")
                
            except Exception as e:
                print(f"   ❌ {endpoint}: Exception - {e}")
        
    except Exception as e:
        print(f"❌ Exception: {e}")

def main():
    """Main function."""
    print("🔍 BEARER TRANSPORT TEST")
    print("=" * 40)
    
    test_bearer_transport_issue()
    
    print(f"\n📊 BEARER TRANSPORT SUMMARY")
    print("=" * 40)
    print("This test helps identify if the issue is with BearerTransport")

if __name__ == "__main__":
    main()
