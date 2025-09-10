#!/usr/bin/env python3
"""
Complete test van soft delete functionaliteit
"""
import asyncio
import httpx
import json

# Configuration
BASE_URL = "https://v2asbest-tool-production.up.railway.app"
JWT_TOKEN = "YOUR_JWT_TOKEN_HERE"  # Vervang dit met je echte JWT token

async def test_soft_delete_complete():
    """Complete test van soft delete functionaliteit"""
    
    if JWT_TOKEN == "YOUR_JWT_TOKEN_HERE":
        print("❌ Stel eerst je JWT token in!")
        print("1. Login op het systeem")
        print("2. Open browser dev tools (F12)")
        print("3. Ga naar Application/Storage")
        print("4. Zoek 'asbest_jwt' in localStorage")
        print("5. Kopieer de token waarde")
        return
    
    headers = {"Authorization": f"Bearer {JWT_TOKEN}"}
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            print("🧪 Complete Soft Delete Test")
            print("=" * 60)
            
            # 1. Test API Health
            print("\n1. Testing API Health...")
            health_response = await client.get(f"{BASE_URL}/healthz")
            if health_response.status_code == 200:
                print("✅ API is healthy")
            else:
                print(f"❌ API Health failed: {health_response.status_code}")
                return
            
            # 2. Haal alle rapporten op
            print("\n2. Ophalen van alle rapporten...")
            reports_response = await client.get(f"{BASE_URL}/reports/", headers=headers)
            if reports_response.status_code != 200:
                print(f"❌ Kan rapporten niet ophalen: {reports_response.status_code}")
                print(f"Response: {reports_response.text}")
                return
            
            reports_data = reports_response.json()
            reports = reports_data.get('items', [])
            total_reports = reports_data.get('total', len(reports))
            
            print(f"📊 Gevonden {len(reports)} rapporten (totaal: {total_reports})")
            
            if not reports:
                print("✅ Geen rapporten om te testen")
                return
            
            # 3. Toon rapport details
            print("\n3. Rapport details:")
            for i, report in enumerate(reports[:3], 1):  # Toon eerste 3
                report_id = report.get('id')
                filename = report.get('filename', 'Unknown')
                status = report.get('status', 'Unknown')
                tenant_name = report.get('tenant_name', 'Unknown')
                
                print(f"   {i}. {filename}")
                print(f"      ID: {report_id}")
                print(f"      Status: {status}")
                print(f"      Tenant: {tenant_name}")
                print()
            
            # 4. Test soft delete op eerste rapport
            test_report = reports[0]
            test_report_id = test_report.get('id')
            test_filename = test_report.get('filename', 'Unknown')
            test_status_before = test_report.get('status', 'Unknown')
            
            print(f"4. Testen soft delete op: {test_filename}")
            print(f"   Report ID: {test_report_id}")
            print(f"   Status voor delete: {test_status_before}")
            
            # Test soft delete
            print("   🗑️  Uitvoeren soft delete...")
            delete_response = await client.delete(f"{BASE_URL}/reports/{test_report_id}", headers=headers)
            
            print(f"   Delete response status: {delete_response.status_code}")
            if delete_response.status_code == 200:
                delete_data = delete_response.json()
                print(f"   ✅ Soft delete succesvol: {delete_data.get('message')}")
                print(f"   Deleted at: {delete_data.get('deleted_at')}")
                
                # Wacht even
                print("   ⏳ Wachten 2 seconden...")
                await asyncio.sleep(2)
                
                # Haal rapporten opnieuw op
                print("   🔄 Ophalen rapporten na delete...")
                reports_response2 = await client.get(f"{BASE_URL}/reports/", headers=headers)
                
                if reports_response2.status_code == 200:
                    reports_data2 = reports_response2.json()
                    reports2 = reports_data2.get('items', [])
                    total_reports2 = reports_data2.get('total', len(reports2))
                    
                    print(f"   📊 Na delete: {len(reports2)} rapporten (totaal: {total_reports2})")
                    
                    # Zoek het verwijderde rapport
                    deleted_report = None
                    for report in reports2:
                        if report.get('id') == test_report_id:
                            deleted_report = report
                            break
                    
                    if deleted_report:
                        print(f"   ❌ PROBLEEM: Rapport nog steeds zichtbaar!")
                        print(f"      Status: {deleted_report.get('status')}")
                        print(f"      Filename: {deleted_report.get('filename')}")
                        print(f"      Tenant: {deleted_report.get('tenant_name')}")
                        
                        # Test directe API call naar specifiek rapport
                        print("   🔍 Testen directe API call naar rapport...")
                        direct_response = await client.get(f"{BASE_URL}/reports/{test_report_id}", headers=headers)
                        if direct_response.status_code == 200:
                            direct_data = direct_response.json()
                            print(f"      Direct API status: {direct_data.get('status')}")
                            print(f"      Direct API deleted_at: {direct_data.get('deleted_at')}")
                        else:
                            print(f"      Direct API failed: {direct_response.status_code}")
                            
                    else:
                        print(f"   ✅ SUCCESS: Rapport niet meer zichtbaar!")
                        
                else:
                    print(f"   ❌ Kan rapporten niet ophalen na delete: {reports_response2.status_code}")
                    print(f"   Response: {reports_response2.text}")
                    
            else:
                print(f"   ❌ Soft delete mislukt: {delete_response.status_code}")
                print(f"   Response: {delete_response.text}")
            
            # 5. Test restore functionaliteit (als delete succesvol was)
            if delete_response.status_code == 200:
                print(f"\n5. Testen restore functionaliteit...")
                restore_response = await client.post(f"{BASE_URL}/reports/{test_report_id}/restore", headers=headers)
                
                if restore_response.status_code == 200:
                    restore_data = restore_response.json()
                    print(f"   ✅ Restore succesvol: {restore_data.get('message')}")
                    
                    # Wacht even
                    await asyncio.sleep(1)
                    
                    # Haal rapporten opnieuw op
                    print("   🔄 Ophalen rapporten na restore...")
                    reports_response3 = await client.get(f"{BASE_URL}/reports/", headers=headers)
                    
                    if reports_response3.status_code == 200:
                        reports_data3 = reports_response3.json()
                        reports3 = reports_data3.get('items', [])
                        
                        # Zoek het gerestaureerde rapport
                        restored_report = None
                        for report in reports3:
                            if report.get('id') == test_report_id:
                                restored_report = report
                                break
                        
                        if restored_report:
                            print(f"   ✅ SUCCESS: Rapport weer zichtbaar na restore!")
                            print(f"      Status: {restored_report.get('status')}")
                        else:
                            print(f"   ❌ PROBLEEM: Rapport niet zichtbaar na restore!")
                    else:
                        print(f"   ❌ Kan rapporten niet ophalen na restore: {reports_response3.status_code}")
                        
                else:
                    print(f"   ❌ Restore mislukt: {restore_response.status_code}")
                    print(f"   Response: {restore_response.text}")
            
            print("\n" + "=" * 60)
            print("🎯 Test Summary:")
            print("- Controleer of soft delete daadwerkelijk werkt")
            print("- Controleer of filtering correct is")
            print("- Controleer of restore functionaliteit werkt")
            
        except Exception as e:
            print(f"❌ Fout: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_soft_delete_complete())
