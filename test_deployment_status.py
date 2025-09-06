#!/usr/bin/env python3
"""
Test script to check deployment status and potential errors.
"""
import requests
import json

# Railway API URL
API_BASE_URL = "https://v2asbest-tool-production.up.railway.app"

def test_deployment_status():
    """Test deployment status and check for errors."""
    try:
        print(f"🔍 Testing deployment status...")
        
        # Test health endpoint
        response = requests.get(f"{API_BASE_URL}/healthz")
        print(f"   /healthz: {response.status_code}")
        
        if response.status_code == 200:
            print(f"      ✅ Health check passed")
        else:
            print(f"      ❌ Health check failed")
            return
        
        # Test root endpoint
        response = requests.get(f"{API_BASE_URL}/")
        print(f"   /: {response.status_code}")
        
        if response.status_code == 200:
            print(f"      ✅ Root endpoint works")
        else:
            print(f"      ❌ Root endpoint failed")
        
        # Test if the issue is with the import
        print(f"\n🔍 Testing if the issue is with the import...")
        
        # Try to access the docs to see if there are any import errors
        response = requests.get(f"{API_BASE_URL}/docs")
        print(f"   /docs: {response.status_code}")
        
        if response.status_code == 200:
            print(f"      ✅ Docs endpoint works - no import errors")
        else:
            print(f"      ❌ Docs endpoint failed - possible import error")
        
        # Test login to see if basic auth still works
        print(f"\n🔍 Testing basic auth functionality...")
        
        response = requests.post(
            f"{API_BASE_URL}/auth/jwt/login",
            data={
                "username": "admin@bedrijfy.nl",
                "password": "Admin123!"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        print(f"   /auth/jwt/login: {response.status_code}")
        
        if response.status_code == 200:
            print(f"      ✅ Login still works")
        else:
            print(f"      ❌ Login failed - possible auth system broken")
            try:
                error_data = response.json()
                print(f"      Error: {json.dumps(error_data, indent=6)}")
            except:
                print(f"      Raw error: {response.text}")
        
    except Exception as e:
        print(f"❌ Exception: {e}")

def main():
    """Main function."""
    print("🔍 DEPLOYMENT STATUS TEST")
    print("=" * 30)
    
    test_deployment_status()
    
    print(f"\n📊 DEPLOYMENT STATUS SUMMARY")
    print("=" * 30)
    print("This test checks if the deployment is working correctly")

if __name__ == "__main__":
    main()
