#!/usr/bin/env python3
"""
Eenvoudige test voor PDF upload.
"""
import requests
import json

# Railway API URL
RAILWAY_URL = "https://v2asbest-tool-production.up.railway.app"

def test_simple_upload():
    """Eenvoudige test voor PDF upload."""
    print("🚀 Eenvoudige PDF Upload Test")
    print("=" * 40)
    
    # 1. Test API health
    try:
        response = requests.get(f"{RAILWAY_URL}/healthz", timeout=5)
        print(f"✅ API Health: {response.status_code}")
    except Exception as e:
        print(f"❌ API Health Error: {e}")
        return
    
    # 2. Test login
    try:
        login_response = requests.post(f"{RAILWAY_URL}/auth/jwt/login", data={
            "username": "admin@bedrijfy.nl",
            "password": "Admin123!"
        }, timeout=10)
        
        if login_response.status_code == 200:
            print("✅ Login successful")
            token = login_response.json().get('access_token')
            headers = {"Authorization": f"Bearer {token}"}
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            return
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    # 3. Test PDF upload
    try:
        with open("test_asbest_rapport.pdf", 'rb') as f:
            files = {'file': (f.name, f, 'application/pdf')}
            response = requests.post(
                f"{RAILWAY_URL}/reports/",
                files=files,
                headers=headers,
                timeout=30
            )
            
            print(f"📄 Upload response: {response.status_code}")
            if response.status_code == 201:
                data = response.json()
                report_id = data.get('id')
                status = data.get('status')
                print(f"✅ Upload successful!")
                print(f"   Report ID: {report_id}")
                print(f"   Status: {status}")
                
                # Check status after 30 seconds
                print("\n⏳ Waiting 30 seconds...")
                import time
                time.sleep(30)
                
                status_response = requests.get(
                    f"{RAILWAY_URL}/reports/{report_id}",
                    headers=headers,
                    timeout=10
                )
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    final_status = status_data.get('status')
                    print(f"📊 Status na 30s: {final_status}")
                    
                    if final_status == 'FAILED':
                        print(f"   Error: {status_data.get('error_message', 'Unknown error')}")
                    elif final_status == 'DONE':
                        print(f"   Score: {status_data.get('score')}")
                        print(f"   Findings: {status_data.get('finding_count')}")
                else:
                    print(f"❌ Status check failed: {status_response.status_code}")
            else:
                print(f"❌ Upload failed: {response.text}")
    except Exception as e:
        print(f"❌ Upload error: {e}")

if __name__ == "__main__":
    test_simple_upload()
