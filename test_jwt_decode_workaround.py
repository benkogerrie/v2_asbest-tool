#!/usr/bin/env python3
"""
Test script to check if we can implement the JWT decode workaround.
"""
import requests
import json
import base64
from datetime import datetime

# Railway API URL
API_BASE_URL = "https://v2asbest-tool-production.up.railway.app"

def test_jwt_decode_workaround():
    """Test if we can implement the JWT decode workaround."""
    try:
        print(f"🔍 Testing JWT decode workaround...")
        
        # Login
        response = requests.post(
            f"{API_BASE_URL}/auth/jwt/login",
            data={
                "username": "admin@bedrijfy.nl",
                "password": "Admin123!"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code != 200:
            print(f"❌ Login failed: {response.status_code}")
            return
        
        token = response.json().get("access_token")
        print(f"✅ Login successful")
        
        # Decode JWT token
        print(f"\n🔍 Decoding JWT token...")
        
        try:
            # Split token into header, payload, signature
            header_encoded, payload_encoded, signature_encoded = token.split('.')
            
            # Decode header and payload
            header_decoded = base64.b64decode(header_encoded + '==').decode('utf-8')
            payload_decoded = base64.b64decode(payload_encoded + '==').decode('utf-8')
            
            header = json.loads(header_decoded)
            payload = json.loads(payload_decoded)
            
            print(f"   JWT Header: {json.dumps(header, indent=2)}")
            print(f"   JWT Payload: {json.dumps(payload, indent=2)}")
            
            # Extract user ID from payload
            user_id = payload.get("sub")
            print(f"   User ID from JWT: {user_id}")
            
            # Check expiration
            exp_timestamp = payload.get("exp")
            if exp_timestamp:
                exp_datetime = datetime.fromtimestamp(exp_timestamp)
                print(f"   Token expires: {exp_datetime}")
                print(f"   Current time: {datetime.now()}")
                print(f"   Token valid: {datetime.now() < exp_datetime}")
            else:
                print("   Token has no expiration (exp) claim.")
            
            print(f"\n✅ JWT decode successful - we can implement the workaround")
            print(f"   The JWT contains user ID: {user_id}")
            print(f"   We can use this to load the user from the database")
            
        except Exception as e:
            print(f"❌ Failed to decode JWT token: {e}")
            return
        
        # Test if the workaround would work
        print(f"\n🔍 Testing if the workaround would work...")
        
        # Test /users/me to see the user structure
        response = requests.get(
            f"{API_BASE_URL}/users/me",
            headers={'Authorization': f'Bearer {token}'}
        )
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"   User data from /users/me: {json.dumps(user_data, indent=2)}")
            print(f"   User ID from /users/me: {user_data.get('id')}")
            print(f"   User ID from JWT: {user_id}")
            
            if user_data.get('id') == user_id:
                print(f"   ✅ User IDs match - workaround would work")
            else:
                print(f"   ❌ User IDs don't match - workaround might not work")
        else:
            print(f"   ❌ /users/me failed: {response.status_code}")
        
    except Exception as e:
        print(f"❌ Exception: {e}")

def main():
    """Main function."""
    print("🔍 JWT DECODE WORKAROUND TEST")
    print("=" * 35)
    
    test_jwt_decode_workaround()
    
    print(f"\n📊 JWT DECODE WORKAROUND SUMMARY")
    print("=" * 35)
    print("This test checks if we can implement the JWT decode workaround")

if __name__ == "__main__":
    main()
