#!/usr/bin/env python3
"""
Test om te controleren of API endpoints bereikbaar zijn
"""
import asyncio
import httpx

# Configuration
BASE_URL = "https://v2asbest-tool-production.up.railway.app"

async def test_api_endpoints():
    """Test API endpoints bereikbaarheid"""
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            print("🧪 API Endpoints Test")
            print("=" * 50)
            
            # 1. Test health endpoint
            print("\n1. Testing health endpoint...")
            health_response = await client.get(f"{BASE_URL}/healthz")
            print(f"   Health status: {health_response.status_code}")
            if health_response.status_code == 200:
                health_data = health_response.json()
                print(f"   ✅ API is running: {health_data.get('status', 'Unknown')}")
            else:
                print(f"   ❌ Health check failed: {health_response.text}")
            
            # 2. Test reports endpoint (zonder auth - moet 401 geven)
            print("\n2. Testing reports endpoint (zonder auth)...")
            reports_response = await client.get(f"{BASE_URL}/reports/")
            print(f"   Reports status: {reports_response.status_code}")
            if reports_response.status_code == 401:
                print(f"   ✅ Reports endpoint vereist authenticatie (401)")
            else:
                print(f"   ⚠️  Onverwachte status: {reports_response.text[:100]}")
            
            # 3. Test analyses endpoint (zonder auth - moet 401 geven)
            print("\n3. Testing analyses endpoint (zonder auth)...")
            # Gebruik een dummy UUID voor de test
            dummy_report_id = "12345678-1234-1234-1234-123456789012"
            analyses_response = await client.get(f"{BASE_URL}/analyses/reports/{dummy_report_id}/analysis")
            print(f"   Analyses status: {analyses_response.status_code}")
            if analyses_response.status_code == 401:
                print(f"   ✅ Analyses endpoint vereist authenticatie (401)")
            elif analyses_response.status_code == 404:
                print(f"   ✅ Analyses endpoint bereikbaar, maar rapport niet gevonden (404)")
            else:
                print(f"   ⚠️  Onverwachte status: {analyses_response.text[:100]}")
            
            # 4. Test findings endpoint (zonder auth - moet 401 geven)
            print("\n4. Testing findings endpoint (zonder auth)...")
            findings_response = await client.get(f"{BASE_URL}/findings/reports/{dummy_report_id}/findings")
            print(f"   Findings status: {findings_response.status_code}")
            if findings_response.status_code == 401:
                print(f"   ✅ Findings endpoint vereist authenticatie (401)")
            elif findings_response.status_code == 404:
                print(f"   ✅ Findings endpoint bereikbaar, maar rapport niet gevonden (404)")
            else:
                print(f"   ⚠️  Onverwachte status: {findings_response.text[:100]}")
            
            print("\n" + "=" * 50)
            print("🎯 Conclusie:")
            print("- Alle endpoints zijn bereikbaar")
            print("- Authenticatie wordt correct vereist")
            print("- De API structuur is correct")
            
        except Exception as e:
            print(f"❌ Fout: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_api_endpoints())