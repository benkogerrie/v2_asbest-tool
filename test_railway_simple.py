#!/usr/bin/env python3
"""
Eenvoudige Railway cloud test
"""
import requests
import json

# Vervang met je echte Railway URL
RAILWAY_URL = "https://v2asbest-tool-production.up.railway.app"

def test_railway():
    """Test Railway deployment"""
    print("🚀 Railway Cloud Test")
    print("=" * 40)
    print(f"URL: {RAILWAY_URL}")
    print()
    
    if "your-railway-app" in RAILWAY_URL:
        print("❌ Update RAILWAY_URL met je echte Railway URL")
        return
    
    try:
        # Test health endpoint
        print("🏥 Testing health endpoint...")
        response = requests.get(f"{RAILWAY_URL}/healthz", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Health: {data.get('status', 'unknown')}")
            print(f"   📊 Database: {data.get('checks', {}).get('database', 'unknown')}")
            print(f"   📊 Redis: {data.get('checks', {}).get('redis', 'unknown')}")
        else:
            print(f"   ❌ Health check failed: {response.text}")
        
        # Test API root
        print("\n🔗 Testing API root...")
        response = requests.get(f"{RAILWAY_URL}/", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ API is responding")
        else:
            print(f"   ⚠️  API response: {response.text[:100]}")
        
        print("\n🎉 Railway test completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_railway()
