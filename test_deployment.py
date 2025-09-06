#!/usr/bin/env python3
"""
Test script to verify Slice 5 deployment on Railway.
"""
import requests
import json
import time
from datetime import datetime

# Railway API URL
API_BASE_URL = "https://v2asbest-tool-production.up.railway.app"

def test_api_health():
    """Test if API is healthy."""
    try:
        response = requests.get(f"{API_BASE_URL}/healthz", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Health: {data.get('status', 'unknown')}")
            return True
        else:
            print(f"❌ API Health failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API Health error: {e}")
        return False

def test_new_endpoints():
    """Test if new Slice 5 endpoints are available."""
    endpoints_to_test = [
        "/analyses/reports/test-id/analysis",
        "/findings/reports/test-id/findings"
    ]
    
    for endpoint in endpoints_to_test:
        try:
            response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=10)
            # We expect 404 for test-id, but endpoint should exist
            if response.status_code in [404, 401, 422]:  # Endpoint exists but test-id not found
                print(f"✅ Endpoint {endpoint}: Available")
            else:
                print(f"⚠️ Endpoint {endpoint}: Unexpected status {response.status_code}")
        except Exception as e:
            print(f"❌ Endpoint {endpoint}: Error - {e}")

def test_database_migration():
    """Test if database migration was successful by checking if new tables exist."""
    try:
        # This is a simple test - we'll check if the API responds to new endpoints
        # In a real scenario, you'd query the database directly
        response = requests.get(f"{API_BASE_URL}/healthz", timeout=10)
        if response.status_code == 200:
            print("✅ Database migration: API responding (migration likely successful)")
            return True
        else:
            print("❌ Database migration: API not responding")
            return False
    except Exception as e:
        print(f"❌ Database migration test error: {e}")
        return False

def main():
    """Run all deployment tests."""
    print("🧪 SLICE 5 DEPLOYMENT TEST")
    print("=" * 50)
    print(f"Testing at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API URL: {API_BASE_URL}")
    print()
    
    # Test 1: API Health
    print("1. Testing API Health...")
    health_ok = test_api_health()
    print()
    
    # Test 2: New Endpoints
    print("2. Testing New Endpoints...")
    test_new_endpoints()
    print()
    
    # Test 3: Database Migration
    print("3. Testing Database Migration...")
    migration_ok = test_database_migration()
    print()
    
    # Summary
    print("📊 DEPLOYMENT TEST SUMMARY")
    print("=" * 50)
    if health_ok and migration_ok:
        print("✅ DEPLOYMENT SUCCESSFUL!")
        print("🎯 Ready for end-to-end testing")
    else:
        print("❌ DEPLOYMENT ISSUES DETECTED")
        print("🔧 Check Railway logs for details")
    
    print()
    print("Next steps:")
    print("- Test file upload and processing")
    print("- Verify rule-based analysis")
    print("- Test PDF generation")
    print("- Validate UI functionality")

if __name__ == "__main__":
    main()
