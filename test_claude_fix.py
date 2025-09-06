#!/usr/bin/env python3
"""
Test script to verify Claude's solution resolves the FastAPI Users dependency problem.
"""
import requests
import json

# Railway API URL
API_BASE_URL = "https://v2asbest-tool-production.up.railway.app"

# Test credentials
TEST_EMAIL = "admin@bedrijfy.nl"
TEST_PASSWORD = "Admin123!"
SYSTEM_EMAIL = "system@asbest-tool.nl"
SYSTEM_PASSWORD = "SystemOwner123!"

def test_claude_fix():
    """Test if Claude's solution resolves the FastAPI Users dependency problem."""
    try:
        print(f"🔍 Testing Claude's solution...")
        
        # Test with admin user
        print(f"\n🔍 Testing with admin user...")
        
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
            print(f"❌ Admin login failed: {response.status_code}")
            return
        
        token = response.json().get("access_token")
        print(f"✅ Admin login successful")
        
        # Test the previously failing endpoints
        print(f"\n🔍 Testing previously failing endpoints...")
        
        endpoints = [
            ("/users/me", "FastAPI Users default endpoint (should work)"),
            ("/reports", "Custom endpoint with get_current_active_user"),
            ("/tenants", "Custom endpoint with get_current_system_owner"),
            ("/analyses/reports/test-id/analysis", "Custom endpoint with get_current_active_user"),
            ("/findings/reports/test-id/findings", "Custom endpoint with get_current_active_user")
        ]
        
        success_count = 0
        total_count = len(endpoints)
        
        for endpoint, description in endpoints:
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
                elif response.status_code == 422:
                    print(f"      ⚠️ 422 Validation Error (expected for invalid UUID)")
                    success_count += 1  # 422 is expected for invalid UUID
                elif response.status_code in [200, 201]:
                    print(f"      ✅ Success - Fixed!")
                    success_count += 1
                else:
                    print(f"      ⚠️ Unexpected status: {response.status_code}")
                
            except Exception as e:
                print(f"   ❌ {endpoint}: Exception - {e}")
        
        # Test with system owner
        print(f"\n🔍 Testing with system owner...")
        
        system_response = requests.post(
            f"{API_BASE_URL}/auth/jwt/login",
            data={
                "username": SYSTEM_EMAIL,
                "password": SYSTEM_PASSWORD
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
                try:
                    error_data = response.json()
                    print(f"      Error: {json.dumps(error_data, indent=6)}")
                except:
                    print(f"      Raw error: {response.text}")
            elif response.status_code in [200, 201]:
                print(f"      ✅ Success - System owner works!")
                success_count += 1
            else:
                print(f"      ⚠️ Unexpected status: {response.status_code}")
        else:
            print(f"❌ System owner login failed: {system_response.status_code}")
        
        # Test reports endpoint with system owner
        if system_response.status_code == 200:
            response = requests.get(
                f"{API_BASE_URL}/reports",
                headers={'Authorization': f'Bearer {system_token}'}
            )
            
            print(f"   /reports (system owner): {response.status_code}")
            
            if response.status_code == 401:
                print(f"      ❌ 401 Unauthorized - System owner reports still failing")
            elif response.status_code in [200, 201]:
                print(f"      ✅ Success - System owner reports work!")
                success_count += 1
            else:
                print(f"      ⚠️ Unexpected status: {response.status_code}")
        
        # Summary
        print(f"\n📊 CLAUDE'S SOLUTION SUMMARY")
        print("=" * 40)
        print(f"Success rate: {success_count}/{total_count + 2} endpoints working")
        
        if success_count >= total_count:
            print(f"🎉 SUCCESS! Claude's solution works!")
            print(f"   FastAPI Users dependency problem is resolved")
        else:
            print(f"❌ FAILED! Claude's solution doesn't work")
            print(f"   FastAPI Users dependency problem persists")
        
    except Exception as e:
        print(f"❌ Exception: {e}")

def main():
    """Main function."""
    print("🔍 CLAUDE'S SOLUTION TEST")
    print("=" * 30)
    
    test_claude_fix()
    
    print(f"\n📊 CLAUDE'S SOLUTION SUMMARY")
    print("=" * 30)
    print("This test verifies if Claude's solution resolves the FastAPI Users dependency problem")

if __name__ == "__main__":
    main()
