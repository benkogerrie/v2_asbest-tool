#!/usr/bin/env python3
"""
Test script to decode and analyze JWT token.
"""
import requests
import json
import base64
from datetime import datetime

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

def decode_jwt_token(token):
    """Decode JWT token without verification to see contents."""
    try:
        # Split token into parts
        parts = token.split('.')
        if len(parts) != 3:
            print("❌ Invalid JWT token format")
            return None
        
        # Decode header
        header_data = base64.urlsafe_b64decode(parts[0] + '==').decode('utf-8')
        header = json.loads(header_data)
        print(f"🔍 JWT Header: {json.dumps(header, indent=2)}")
        
        # Decode payload
        payload_data = base64.urlsafe_b64decode(parts[1] + '==').decode('utf-8')
        payload = json.loads(payload_data)
        print(f"🔍 JWT Payload: {json.dumps(payload, indent=2)}")
        
        # Check expiration
        if 'exp' in payload:
            exp_timestamp = payload['exp']
            exp_datetime = datetime.fromtimestamp(exp_timestamp)
            now = datetime.now()
            print(f"🔍 Token expires: {exp_datetime}")
            print(f"🔍 Current time: {now}")
            print(f"🔍 Token valid: {exp_datetime > now}")
        
        return payload
        
    except Exception as e:
        print(f"❌ Error decoding token: {e}")
        return None

def test_token_with_different_endpoints(token):
    """Test token with different endpoints to see which ones work."""
    endpoints = [
        "/users/me",
        "/reports",
        "/healthz",
        "/analyses/reports/test-id/analysis"
    ]
    
    print(f"\n🧪 Testing token with different endpoints...")
    
    for endpoint in endpoints:
        try:
            response = requests.get(
                f"{API_BASE_URL}{endpoint}",
                headers={'Authorization': f'Bearer {token}'}
            )
            
            status_emoji = "✅" if response.status_code in [200, 201] else "❌"
            print(f"   {status_emoji} {endpoint}: {response.status_code}")
            
            if response.status_code not in [200, 201]:
                print(f"      Response: {response.text[:100]}...")
                
        except Exception as e:
            print(f"   ❌ {endpoint}: Exception - {e}")

def main():
    """Main function."""
    print("🔍 JWT TOKEN ANALYSIS")
    print("=" * 40)
    
    # Login
    token = login()
    if not token:
        return
    
    # Decode token
    print(f"\n1. Decoding JWT token...")
    payload = decode_jwt_token(token)
    
    # Test with different endpoints
    print(f"\n2. Testing token with different endpoints...")
    test_token_with_different_endpoints(token)
    
    print("\n📊 TOKEN ANALYSIS SUMMARY")
    print("=" * 40)
    print("This helps identify JWT token issues")

if __name__ == "__main__":
    main()
