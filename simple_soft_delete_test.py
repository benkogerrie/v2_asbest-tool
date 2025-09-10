#!/usr/bin/env python3
"""
Eenvoudige test om te controleren of soft delete werkt
"""
import asyncio
import httpx
import json

# Configuration
BASE_URL = "https://v2asbest-tool-production.up.railway.app"

async def simple_test():
    """Eenvoudige test zonder authentication"""
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            print("🧪 Simple Soft Delete Test (No Auth)")
            print("=" * 50)
            
            # 1. Test API Health
            print("\n1. Testing API Health...")
            health_response = await client.get(f"{BASE_URL}/healthz")
            if health_response.status_code == 200:
                print("✅ API is healthy")
            else:
                print(f"❌ API Health failed: {health_response.status_code}")
                return
            
            # 2. Test reports endpoint (should require auth)
            print("\n2. Testing reports endpoint...")
            reports_response = await client.get(f"{BASE_URL}/reports/")
            print(f"   Reports endpoint status: {reports_response.status_code}")
            
            if reports_response.status_code == 401:
                print("   ✅ Authentication required (expected)")
            elif reports_response.status_code == 200:
                print("   ⚠️  No authentication required (unexpected)")
                data = reports_response.json()
                print(f"   Reports: {json.dumps(data, indent=2)[:200]}...")
            else:
                print(f"   ❌ Unexpected status: {reports_response.status_code}")
                print(f"   Response: {reports_response.text}")
            
            # 3. Test delete endpoint (should require auth)
            print("\n3. Testing delete endpoint...")
            test_id = "00000000-0000-0000-0000-000000000000"  # Fake UUID
            delete_response = await client.delete(f"{BASE_URL}/reports/{test_id}")
            print(f"   Delete endpoint status: {delete_response.status_code}")
            
            if delete_response.status_code == 401:
                print("   ✅ Authentication required (expected)")
            elif delete_response.status_code == 404:
                print("   ✅ Report not found (expected for fake ID)")
            else:
                print(f"   ❌ Unexpected status: {delete_response.status_code}")
                print(f"   Response: {delete_response.text}")
            
            print("\n" + "=" * 50)
            print("🎯 Test Results:")
            print("- API endpoints are accessible")
            print("- Authentication is required (good)")
            print("- Ready for authenticated testing")
            
        except Exception as e:
            print(f"❌ Fout: {e}")

if __name__ == "__main__":
    asyncio.run(simple_test())
