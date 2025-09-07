#!/usr/bin/env python3
"""
Enhanced test script with detailed debugging.
"""

import requests
import json

BASE_URL = 'https://v2asbest-tool-production.up.railway.app'

def test_authentication_chain():
    """Test the entire authentication chain step by step."""
    
    print("🔐 Testing Authentication Chain...")
    
    # Test with tenant admin credentials
    username = "admin@bedrijfy.nl"
    password = "Admin123!"
    
    print(f"\n1️⃣ Testing login...")
    try:
        response = requests.post(f"{BASE_URL}/auth/jwt/login", data={
            "username": username,
            "password": password
        })
        
        if response.status_code == 200:
            print(f"✅ Login successful")
            token_data = response.json()
            token = token_data.get('access_token')
            print(f"   Token type: {token_data.get('token_type')}")
            print(f"   Token length: {len(token) if token else 'None'}")
            
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test 2: /users/me (known working endpoint)
            print(f"\n2️⃣ Testing /users/me...")
            response = requests.get(f"{BASE_URL}/users/me", headers=headers)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                user_info = response.json()
                print(f"   ✅ User info retrieved successfully")
                print(f"   - ID: {user_info.get('id')}")
                print(f"   - Email: {user_info.get('email')}")
                print(f"   - Role: {user_info.get('role')}")
                print(f"   - Active: {user_info.get('is_active')}")
                print(f"   - Tenant ID: {user_info.get('tenant_id')}")
            else:
                print(f"   ❌ Failed: {response.text}")
                return
            
            # Test 3: Original /reports endpoint
            print(f"\n3️⃣ Testing original /reports...")
            response = requests.get(f"{BASE_URL}/reports", headers=headers)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   ✅ Success!")
                reports_data = response.json()
                print(f"   - Total reports: {reports_data.get('total', 0)}")
            else:
                print(f"   ❌ Failed: {response.text}")
                
                # Additional debugging
                print(f"\n🔍 Additional debugging:")
                print(f"   - Response headers: {dict(response.headers)}")
                print(f"   - Request headers sent: {headers}")
                
                # Test if it's a 401 specifically
                if response.status_code == 401:
                    print(f"   - This is a 401 Unauthorized error")
                    print(f"   - Checking if token is being sent correctly...")
                    
                    # Test with malformed token
                    bad_headers = {"Authorization": f"Bearer invalid_token"}
                    response = requests.get(f"{BASE_URL}/reports", headers=bad_headers)
                    print(f"   - Bad token test: {response.status_code}")
                    
                    # Test without Authorization header
                    response = requests.get(f"{BASE_URL}/reports")
                    print(f"   - No auth test: {response.status_code}")
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_token_validation():
    """Test token validation specifically."""
    print("\n🔍 Token Validation Test...")
    
    # Get token
    response = requests.post(f"{BASE_URL}/auth/jwt/login", data={
        "username": "admin@bedrijfy.nl",
        "password": "Admin123!"
    })
    
    if response.status_code == 200:
        token = response.json().get('access_token')
        
        # Test different header formats
        test_cases = [
            ("Bearer " + token, "Standard Bearer format"),
            (token, "Token only (no Bearer)"),
            ("bearer " + token, "Lowercase bearer"),
            ("JWT " + token, "JWT prefix instead of Bearer"),
        ]
        
        for auth_value, description in test_cases:
            headers = {"Authorization": auth_value}
            response = requests.get(f"{BASE_URL}/users/me", headers=headers)
            print(f"   {description}: {response.status_code}")

if __name__ == "__main__":
    test_authentication_chain()
    test_token_validation()
