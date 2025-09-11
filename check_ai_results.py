#!/usr/bin/env python3
"""
Script om de AI analyse resultaten te controleren
"""
import requests
import json

# API Configuration
API_BASE_URL = "https://v2asbest-tool-production.up.railway.app"
REPORT_ID = "ddc6c689-4854-44ee-8aad-0e03920909e9"

def login():
    """Login en krijg JWT token"""
    print("🔐 Inloggen...")
    
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
            print(f"❌ Login mislukt: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def check_report_details(token, report_id):
    """Check rapport details"""
    print(f"\n📊 Rapport details voor {report_id}:")
    
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f"{API_BASE_URL}/reports/{report_id}", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {data.get('status')}")
            print(f"✅ Score: {data.get('score')}")
            print(f"✅ Finding count: {data.get('finding_count')}")
            print(f"✅ Conclusion key: {data.get('conclusion_object_key')}")
            return data
        else:
            print(f"❌ Failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def check_findings(token, report_id):
    """Check findings"""
    print(f"\n🔍 Findings voor {report_id}:")
    
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f"{API_BASE_URL}/reports/{report_id}/findings", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            findings = data.get('findings', [])
            print(f"✅ Aantal findings: {len(findings)}")
            
            for i, finding in enumerate(findings[:5]):  # Show first 5
                print(f"  {i+1}. {finding.get('code')} - {finding.get('title')} ({finding.get('severity')})")
                print(f"     Status: {finding.get('status')}")
                evidence = finding.get('evidence') or finding.get('evidence_snippet') or 'Geen evidence'
                print(f"     Evidence: {evidence[:100]}...")
                print()
            
            return data
        else:
            print(f"❌ Failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def check_analysis(token, report_id):
    """Check analysis data"""
    print(f"\n🧠 Analysis data voor {report_id}:")
    
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f"{API_BASE_URL}/analyses/latest/{report_id}", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Engine: {data.get('engine')}")
            print(f"✅ Engine version: {data.get('engine_version')}")
            print(f"✅ Score: {data.get('score')}")
            print(f"✅ Summary: {data.get('summary', '')[:200]}...")
            print(f"✅ Rules passed: {data.get('rules_passed')}")
            print(f"✅ Rules failed: {data.get('rules_failed')}")
            return data
        else:
            print(f"❌ Failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    print("🔍 AI Analyse Resultaten Checker")
    print("=" * 50)
    
    # Login
    token = login()
    if not token:
        return
    
    # Check report details
    report_data = check_report_details(token, REPORT_ID)
    
    # Check findings
    findings_data = check_findings(token, REPORT_ID)
    
    # Check analysis
    analysis_data = check_analysis(token, REPORT_ID)
    
    print("\n" + "=" * 50)
    print("📋 SAMENVATTING:")
    print(f"   Rapport ID: {REPORT_ID}")
    print(f"   Status: {report_data.get('status') if report_data else 'Unknown'}")
    print(f"   Score: {report_data.get('score') if report_data else 'Unknown'}")
    print(f"   Findings: {len(findings_data.get('findings', [])) if findings_data else 0}")
    print(f"   Engine: {analysis_data.get('engine') if analysis_data else 'Unknown'}")
    
    if analysis_data and analysis_data.get('engine') == 'AI':
        print("✅ AI analyse is uitgevoerd!")
    else:
        print("❌ AI analyse is NIET uitgevoerd - mogelijk fallback naar rules-based!")

if __name__ == "__main__":
    main()
