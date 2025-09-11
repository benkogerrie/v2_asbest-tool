#!/usr/bin/env python3
"""
Test AI analyse na fix
"""
import requests
import json
import time
from pathlib import Path

# API Configuration
API_BASE_URL = "https://v2asbest-tool-production.up.railway.app"
PDF_PATH = r"C:\Users\meteo\Projects\asbest authoratisatie\24.261 v2.0 Snip 13 Gouderak.pdf"

def login():
    """Login en krijg JWT token"""
    login_data = {
        "username": "admin@bedrijfy.nl",
        "password": "Admin123!"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/jwt/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get('access_token')
        else:
            return None
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def upload_pdf(token):
    """Upload PDF"""
    pdf_file = Path(PDF_PATH)
    if not pdf_file.exists():
        print(f"❌ PDF niet gevonden: {PDF_PATH}")
        return None
    
    print(f"📄 PDF uploaden: {pdf_file.name}")
    
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
            
            if response.status_code == 201:
                result = response.json()
                report_id = result.get('id')
                print(f"✅ Upload succesvol! Report ID: {report_id}")
                return report_id
            else:
                print(f"❌ Upload mislukt: {response.status_code}")
                return None
                
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return None

def check_report_status(report_id, token):
    """Check rapport status"""
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f"{API_BASE_URL}/reports/{report_id}", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('status')
        else:
            return None
    except:
        return None

def wait_for_processing(report_id, token, max_wait=300):
    """Wacht op verwerking"""
    print(f"\n⏳ Wachten op AI verwerking...")
    
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
        
        time.sleep(10)
    
    print("⏰ Timeout bereikt")
    return False

def check_analysis_results(report_id, token):
    """Check analyse resultaten"""
    print(f"\n🔍 Analyse Resultaten:")
    
    try:
        headers = {'Authorization': f'Bearer {token}'}
        
        # Check findings
        response = requests.get(f"{API_BASE_URL}/reports/{report_id}/findings", headers=headers)
        if response.status_code == 200:
            data = response.json()
            findings = data.get('findings', [])
            print(f"✅ Aantal findings: {len(findings)}")
            
            # Show first few findings
            for i, finding in enumerate(findings[:3]):
                print(f"  {i+1}. {finding.get('code')} - {finding.get('title')} ({finding.get('severity')})")
                evidence = finding.get('evidence') or finding.get('evidence_snippet') or 'Geen evidence'
                print(f"     Evidence: {evidence[:100]}...")
        
        # Check report details
        response = requests.get(f"{API_BASE_URL}/reports/{report_id}", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Score: {data.get('score')}")
            print(f"✅ Conclusion key: {data.get('conclusion_object_key')}")
            
            # Check if it's AI or rules-based
            if data.get('conclusion_object_key'):
                print("🎉 Conclusie PDF is gegenereerd!")
                return True
            else:
                print("❌ Geen conclusie PDF - mogelijk fallback")
                return False
        
    except Exception as e:
        print(f"❌ Check results error: {e}")
        return False

def main():
    print("🚀 AI Analyse Test (Na Fix)")
    print("=" * 50)
    
    # Login
    token = login()
    if not token:
        return
    
    # Upload PDF
    report_id = upload_pdf(token)
    if not report_id:
        return
    
    # Wait for processing
    if wait_for_processing(report_id, token):
        # Check results
        success = check_analysis_results(report_id, token)
        
        if success:
            print(f"\n🎉 SUCCES! AI analyse werkt nu!")
            print(f"📄 Rapport ID: {report_id}")
            print(f"🔗 Download: {API_BASE_URL}/reports/{report_id}/conclusion")
        else:
            print(f"\n❌ AI analyse werkt nog steeds niet")
    else:
        print(f"\n❌ Verwerking mislukt of timeout")

if __name__ == "__main__":
    main()

