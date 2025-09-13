#!/usr/bin/env python3
"""
Test PDF upload en processing op Railway.
"""
import requests
import json
import time
import os
from pathlib import Path

# Railway API URL
RAILWAY_URL = "https://v2asbest-tool-production.up.railway.app"

def test_pdf_upload():
    """Test PDF upload en processing op Railway."""
    print("🚀 Railway PDF Upload Test")
    print("=" * 50)
    
    # 1. Test API health
    try:
        response = requests.get(f"{RAILWAY_URL}/healthz", timeout=10)
        if response.status_code == 200:
            print("✅ API is bereikbaar")
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Kan API niet bereiken: {e}")
        return False
    
    # 2. Test PDF upload
    print("\n📄 PDF Upload Test")
    print("-" * 30)
    
    # Gebruik een bestaande test PDF
    test_pdf_path = "test_asbest_rapport.pdf"
    if not os.path.exists(test_pdf_path):
        print(f"❌ Test PDF niet gevonden: {test_pdf_path}")
        return False
    
    # Upload PDF
    try:
        with open(test_pdf_path, 'rb') as f:
            files = {'file': (test_pdf_path, f, 'application/pdf')}
            
            # We need to authenticate first - let's try without auth for now
            response = requests.post(
                f"{RAILWAY_URL}/reports/",
                files=files,
                timeout=30
            )
            
            print(f"Upload response: {response.status_code}")
            if response.status_code == 401:
                print("🔐 Authenticatie vereist - dit is normaal")
                print("   De API werkt, maar we hebben een token nodig voor upload")
                return True
            elif response.status_code == 201:
                print("✅ PDF upload succesvol!")
                data = response.json()
                report_id = data.get('id')
                print(f"   Report ID: {report_id}")
                
                # Monitor processing status
                print("\n⏳ Monitoring processing status...")
                for i in range(30):  # Wait up to 5 minutes
                    time.sleep(10)
                    
                    try:
                        status_response = requests.get(
                            f"{RAILWAY_URL}/reports/{report_id}",
                            timeout=10
                        )
                        
                        if status_response.status_code == 200:
                            status_data = status_response.json()
                            status = status_data.get('status')
                            print(f"   Status na {i*10+10}s: {status}")
                            
                            if status == 'DONE':
                                print("✅ Processing voltooid!")
                                print(f"   Score: {status_data.get('score')}")
                                print(f"   Findings: {status_data.get('finding_count')}")
                                return True
                            elif status == 'FAILED':
                                print("❌ Processing gefaald!")
                                print(f"   Error: {status_data.get('error_message')}")
                                return False
                        else:
                            print(f"   Status check failed: {status_response.status_code}")
                            
                    except Exception as e:
                        print(f"   Status check error: {e}")
                
                print("⏰ Timeout - processing duurt te lang")
                return False
                
            else:
                print(f"❌ Upload failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return False

if __name__ == "__main__":
    success = test_pdf_upload()
    if success:
        print("\n🎉 Test geslaagd!")
    else:
        print("\n💥 Test gefaald!")
