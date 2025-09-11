#!/usr/bin/env python3
"""
Script om een PDF te uploaden naar de online v2_asbest-tool API
"""
import requests
import json
import time
import sys
from pathlib import Path

# API Configuration
API_BASE_URL = "https://v2asbest-tool-production.up.railway.app"
PDF_PATH = r"C:\Users\meteo\Projects\asbest authoratisatie\24.261 v2.0 Snip 13 Gouderak.pdf"

def login():
    """Login en krijg JWT token"""
    print("\n🔐 Inloggen...")
    
    # Test credentials from seed script
    login_data = {
        "username": "admin@bedrijfy.nl",  # Tenant admin
        "password": "Admin123!"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/jwt/login",
            data=login_data,  # Use form data for OAuth2
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=30
        )
        
        print(f"📊 Login response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            access_token = result.get('access_token')
            print(f"✅ Login succesvol!")
            return access_token
        else:
            print(f"❌ Login mislukt: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def upload_pdf(token):
    """Upload PDF en wacht op verwerking"""
    
    # Check if PDF exists
    pdf_file = Path(PDF_PATH)
    if not pdf_file.exists():
        print(f"❌ PDF niet gevonden: {PDF_PATH}")
        return None
    
    print(f"📄 PDF gevonden: {pdf_file.name} ({pdf_file.stat().st_size} bytes)")
    
    # Step 2: Upload PDF
    print("\n📤 PDF uploaden...")
    
    try:
        with open(pdf_file, 'rb') as f:
            files = {'file': (pdf_file.name, f, 'application/pdf')}
            headers = {'Authorization': f'Bearer {token}'}
            
            response = requests.post(
                f"{API_BASE_URL}/reports/",
                files=files,
                headers=headers,
                timeout=60
            )
            
            print(f"📊 Upload response status: {response.status_code}")
            print(f"📊 Upload response: {response.text}")
            
            if response.status_code == 201:
                result = response.json()
                report_id = result.get('id')
                print(f"✅ Upload succesvol! Report ID: {report_id}")
                return report_id
            else:
                print(f"❌ Upload mislukt: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return None

def check_report_status(report_id, token):
    """Check de status van het rapport"""
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f"{API_BASE_URL}/reports/{report_id}", headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data.get('status', 'UNKNOWN')
        else:
            print(f"❌ Status check failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Status check error: {e}")
        return None

def wait_for_processing(report_id, token, max_wait=300):
    """Wacht tot het rapport verwerkt is"""
    print(f"\n⏳ Wachten op verwerking van rapport {report_id}...")
    
    start_time = time.time()
    while time.time() - start_time < max_wait:
        status = check_report_status(report_id, token)
        if status:
            print(f"📊 Status: {status}")
            
            if status == 'DONE':
                print("✅ Verwerking voltooid!")
                return True
            elif status == 'FAILED':
                print("❌ Verwerking mislukt!")
                return False
            elif status == 'PROCESSING':
                print("🔄 Nog aan het verwerken...")
            else:
                print(f"❓ Onbekende status: {status}")
        
        time.sleep(10)  # Check every 10 seconds
    
    print("⏰ Timeout bereikt")
    return False

def get_conclusion_download_url(report_id, token):
    """Krijg de download URL voor de conclusie PDF"""
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f"{API_BASE_URL}/reports/{report_id}/download", headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data.get('url')
        else:
            print(f"❌ Download URL failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Download URL error: {e}")
        return None

def main():
    print("🚀 v2_asbest-tool PDF Upload Test")
    print("=" * 50)
    
    # Step 1: Login
    token = login()
    if not token:
        print("❌ Login mislukt, stoppen...")
        return
    
    # Step 2: Upload PDF
    report_id = upload_pdf(token)
    if not report_id:
        print("❌ Upload mislukt, stoppen...")
        return
    
    # Step 3: Wait for processing
    if wait_for_processing(report_id, token):
        # Step 4: Get download URL
        download_url = get_conclusion_download_url(report_id, token)
        if download_url:
            print(f"\n🎉 SUCCES!")
            print(f"📄 Rapport ID: {report_id}")
            print(f"🔗 Conclusie PDF download URL: {download_url}")
            print(f"\n💡 Je kunt de conclusie PDF downloaden via:")
            print(f"   {API_BASE_URL}/reports/{report_id}/conclusion")
        else:
            print("❌ Kon download URL niet krijgen")
    else:
        print("❌ Verwerking mislukt of timeout")

if __name__ == "__main__":
    main()
