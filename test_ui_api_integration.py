#!/usr/bin/env python3
"""
Test om te controleren of UI en API correct geïntegreerd zijn
"""
import asyncio
import httpx
import json

# Configuration
BASE_URL = "https://v2asbest-tool-production.up.railway.app"
JWT_TOKEN = "YOUR_JWT_TOKEN_HERE"  # Vervang dit met je echte JWT token

async def test_ui_api_integration():
    """Test UI-API integratie"""
    
    if JWT_TOKEN == "YOUR_JWT_TOKEN_HERE":
        print("❌ Stel eerst je JWT token in!")
        return
    
    headers = {"Authorization": f"Bearer {JWT_TOKEN}"}
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            print("🧪 UI-API Integration Test")
            print("=" * 50)
            
            # 1. Test reports endpoint
            print("\n1. Testing reports endpoint...")
            reports_response = await client.get(f"{BASE_URL}/reports/", headers=headers)
            if reports_response.status_code == 200:
                reports_data = reports_response.json()
                reports = reports_data.get('items', [])
                print(f"✅ Reports endpoint: {len(reports)} rapporten")
                
                if reports:
                    test_report = reports[0]
                    test_report_id = test_report.get('id')
                    test_filename = test_report.get('filename', 'Unknown')
                    
                    print(f"   Test rapport: {test_filename}")
                    print(f"   Report ID: {test_report_id}")
                    
                    # 2. Test analyses endpoint
                    print(f"\n2. Testing analyses endpoint...")
                    analyses_response = await client.get(f"{BASE_URL}/analyses/reports/{test_report_id}/analysis", headers=headers)
                    print(f"   Analyses endpoint status: {analyses_response.status_code}")
                    
                    if analyses_response.status_code == 200:
                        analyses_data = analyses_response.json()
                        print(f"   ✅ Analyses endpoint: {analyses_data.get('engine', 'Unknown')}")
                        print(f"   Score: {analyses_data.get('score', 'N/A')}")
                    elif analyses_response.status_code == 404:
                        print(f"   ⚠️  Geen analyse gevonden voor dit rapport")
                    else:
                        print(f"   ❌ Analyses endpoint failed: {analyses_response.text}")
                    
                    # 3. Test findings endpoint
                    print(f"\n3. Testing findings endpoint...")
                    findings_response = await client.get(f"{BASE_URL}/findings/reports/{test_report_id}/findings", headers=headers)
                    print(f"   Findings endpoint status: {findings_response.status_code}")
                    
                    if findings_response.status_code == 200:
                        findings_data = findings_response.json()
                        findings = findings_data.get('findings', [])
                        print(f"   ✅ Findings endpoint: {len(findings)} findings")
                        
                        if findings:
                            print(f"   Eerste finding: {findings[0].get('message', 'Unknown')[:50]}...")
                        else:
                            print(f"   Geen findings gevonden")
                    elif findings_response.status_code == 404:
                        print(f"   ⚠️  Geen findings gevonden voor dit rapport")
                    else:
                        print(f"   ❌ Findings endpoint failed: {findings_response.text}")
                    
                    # 4. Test report detail endpoint
                    print(f"\n4. Testing report detail endpoint...")
                    detail_response = await client.get(f"{BASE_URL}/reports/{test_report_id}", headers=headers)
                    print(f"   Report detail status: {detail_response.status_code}")
                    
                    if detail_response.status_code == 200:
                        detail_data = detail_response.json()
                        print(f"   ✅ Report detail: {detail_data.get('filename', 'Unknown')}")
                        print(f"   Status: {detail_data.get('status', 'Unknown')}")
                        print(f"   Score: {detail_data.get('score', 'N/A')}")
                    else:
                        print(f"   ❌ Report detail failed: {detail_response.text}")
                    
                else:
                    print("   ⚠️  Geen rapporten om te testen")
            else:
                print(f"❌ Reports endpoint failed: {reports_response.status_code}")
                print(f"Response: {reports_response.text}")
            
            print("\n" + "=" * 50)
            print("🎯 Test Summary:")
            print("- Controleer of alle endpoints bereikbaar zijn")
            print("- Controleer of de data correct wordt geretourneerd")
            print("- Controleer of de UI de juiste endpoints aanroept")
            
        except Exception as e:
            print(f"❌ Fout: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_ui_api_integration())
