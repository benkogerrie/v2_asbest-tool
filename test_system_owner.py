#!/usr/bin/env python3
"""
Test script to test with system owner credentials.
"""
import requests
import json

# Railway API URL
API_BASE_URL = "https://v2asbest-tool-production.up.railway.app"

# System owner credentials
SYSTEM_EMAIL = "system@asbest-tool.nl"
SYSTEM_PASSWORD = "SystemOwner123!"

def login():
    """Login and get JWT token."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/jwt/login",
            data={
                "username": SYSTEM_EMAIL,
                "password": SYSTEM_PASSWORD
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print(f"✅ System owner login successful: {SYSTEM_EMAIL}")
            return token
        else:
            print(f"❌ System owner login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ System owner login error: {e}")
        return None

def test_endpoints_with_system_owner(token):
    """Test endpoints with system owner token."""
    endpoints = [
        "/users/me",
        "/reports",
        "/tenants",
        "/analyses/reports/test-id/analysis",
        "/findings/reports/test-id/findings"
    ]
    
    print(f"\n🧪 Testing endpoints with system owner...")
    
    for endpoint in endpoints:
        try:
            response = requests.get(
                f"{API_BASE_URL}{endpoint}",
                headers={'Authorization': f'Bearer {token}'}
            )
            
            status_emoji = "✅" if response.status_code in [200, 201] else "❌"
            print(f"   {status_emoji} {endpoint}: {response.status_code}")
            
            if response.status_code == 200:
                if endpoint == "/users/me":
                    data = response.json()
                    print(f"      Role: {data.get('role')}")
                    print(f"      Tenant ID: {data.get('tenant_id')}")
                elif endpoint == "/reports":
                    data = response.json()
                    print(f"      Reports found: {len(data.get('items', []))}")
                elif endpoint == "/tenants":
                    data = response.json()
                    print(f"      Tenants found: {len(data)}")
            elif response.status_code not in [404, 422]:
                print(f"      Response: {response.text[:100]}...")
                
        except Exception as e:
            print(f"   ❌ {endpoint}: Exception - {e}")

def main():
    """Main function."""
    print("🔍 SYSTEM OWNER TEST")
    print("=" * 30)
    
    # Login as system owner
    token = login()
    if not token:
        return
    
    # Test endpoints
    test_endpoints_with_system_owner(token)
    
    print("\n📊 SYSTEM OWNER TEST SUMMARY")
    print("=" * 30)
    print("This helps identify if the issue is role-specific")

if __name__ == "__main__":
    main()
