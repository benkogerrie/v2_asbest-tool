#!/usr/bin/env python3
"""
Test PDF upload en processing op Railway met tenant admin credentials.
"""
import requests
import json
import time
import os
from pathlib import Path

# Railway API URL
RAILWAY_URL = "https://v2asbest-tool-production.up.railway.app"

# Tenant admin credentials
TENANT_ADMIN_EMAIL = "admin@bedrijfy.nl"
TENANT_ADMIN_PASSWORD = "Admin123!"

def test_pdf_upload_with_auth():
    """Test PDF upload en processing op Railway met authenticatie."""
    print("🚀 Railway PDF Upload Test met Authenticatie")
    print("=" * 60)
    
    # 1. Login als tenant admin
    print("🔐 Logging in als tenant admin...")
    try:
        login_response = requests.post(f"{RAILWAY_URL}/auth/jwt/login", data={
            "username": TENANT_ADMIN_EMAIL,
            "password": TENANT_ADMIN_PASSWORD
        }, timeout=10)
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"Response: {login_response.text}")
            return False
        
        token_data = login_response.json()
        token = token_data.get('access_token')
        if not token:
            print("❌ No access token received")
            return False
        
        print("✅ Login successful!")
        
        # Get user info
        headers = {"Authorization": f"Bearer {token}"}
        user_response = requests.get(f"{RAILWAY_URL}/users/me", headers=headers, timeout=10)
        if user_response.status_code == 200:
            user_info = user_response.json()
            print(f"   User: {user_info.get('first_name')} {user_info.get('last_name')}")
            print(f"   Role: {user_info.get('role')}")
            print(f"   Tenant: {user_info.get('tenant_name', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False
    
    # 2. Test PDF upload
    print("\n📄 PDF Upload Test")
    print("-" * 30)
    
    # Gebruik een bestaande test PDF
    test_pdf_path = "test_asbest_rapport.pdf"
    if not os.path.exists(test_pdf_path):
        print(f"❌ Test PDF niet gevonden: {test_pdf_path}")
        return False
    
    print(f"📁 Uploading: {test_pdf_path}")
    
    try:
        with open(test_pdf_path, 'rb') as f:
            files = {'file': (test_pdf_path, f, 'application/pdf')}
            
            response = requests.post(
                f"{RAILWAY_URL}/reports/",
                files=files,
                headers=headers,
                timeout=30
            )
            
            print(f"Upload response: {response.status_code}")
            if response.status_code == 201:
                print("✅ PDF upload succesvol!")
                data = response.json()
                report_id = data.get('id')
                status = data.get('status')
                print(f"   Report ID: {report_id}")
                print(f"   Status: {status}")
                
                # Monitor processing status
                print("\n⏳ Monitoring processing status...")
                for i in range(30):  # Wait up to 5 minutes
                    time.sleep(10)
                    
                    try:
                        status_response = requests.get(
                            f"{RAILWAY_URL}/reports/{report_id}",
                            headers=headers,
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
                                print(f"   Summary: {status_data.get('summary', 'N/A')[:100]}...")
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
    success = test_pdf_upload_with_auth()
    if success:
        print("\n🎉 PDF processing test geslaagd!")
    else:
        print("\n💥 PDF processing test gefaald!")
