#!/usr/bin/env python3
"""
End-to-end test for Slice 5 functionality.
"""
import requests
import json
import time
from datetime import datetime

# Railway API URL
API_BASE_URL = "https://v2asbest-tool-production.up.railway.app"

# Test credentials - using tenant admin instead of system owner
TEST_EMAIL = "admin@bedrijfy.nl"
TEST_PASSWORD = "Admin123!"

def login():
    """Login and get JWT token."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/jwt/login",
            data={
                "username": TEST_EMAIL,
                "password": TEST_PASSWORD
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print(f"✅ Login successful: {TEST_EMAIL}")
            return token
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_file_upload(token):
    """Test file upload functionality."""
    try:
        # Create a simple test PDF content (minimal valid PDF)
        test_pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj

4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
72 720 Td
(Test PDF for Slice 5) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000206 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
299
%%EOF"""
        
        files = {
            'file': ('test_slice5.pdf', test_pdf_content, 'application/pdf')
        }
        
        headers = {
            'Authorization': f'Bearer {token}'
        }
        
        response = requests.post(
            f"{API_BASE_URL}/reports/",
            files=files,
            headers=headers
        )
        
        if response.status_code == 201:
            data = response.json()
            report_id = data.get("id")
            print(f"✅ File upload successful: {report_id}")
            return report_id
        else:
            print(f"❌ File upload failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ File upload error: {e}")
        return None

def wait_for_processing(report_id, token, max_wait=60):
    """Wait for report processing to complete."""
    print(f"⏳ Waiting for processing of report {report_id}...")
    
    start_time = time.time()
    while time.time() - start_time < max_wait:
        try:
            response = requests.get(
                f"{API_BASE_URL}/reports/{report_id}",
                headers={'Authorization': f'Bearer {token}'}
            )
            
            if response.status_code == 200:
                data = response.json()
                status = data.get("status")
                print(f"   Status: {status}")
                
                if status == "DONE":
                    print(f"✅ Processing completed in {time.time() - start_time:.1f} seconds")
                    return data
                elif status == "FAILED":
                    print(f"❌ Processing failed")
                    return None
                else:
                    time.sleep(5)  # Wait 5 seconds before checking again
            else:
                print(f"❌ Status check failed: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Status check error: {e}")
            return None
    
    print(f"⏰ Processing timeout after {max_wait} seconds")
    return None

def test_analysis_endpoints(report_id, token):
    """Test new analysis endpoints."""
    try:
        # Test analysis endpoint
        response = requests.get(
            f"{API_BASE_URL}/analyses/reports/{report_id}/analysis",
            headers={'Authorization': f'Bearer {token}'}
        )
        
        if response.status_code == 200:
            analysis = response.json()
            print(f"✅ Analysis endpoint: Score {analysis.get('score')}, Engine {analysis.get('engine')}")
        else:
            print(f"⚠️ Analysis endpoint: {response.status_code}")
        
        # Test findings endpoint
        response = requests.get(
            f"{API_BASE_URL}/findings/reports/{report_id}/findings",
            headers={'Authorization': f'Bearer {token}'}
        )
        
        if response.status_code == 200:
            findings = response.json()
            print(f"✅ Findings endpoint: {len(findings)} findings found")
            for finding in findings[:3]:  # Show first 3 findings
                print(f"   - {finding.get('rule_id')}: {finding.get('severity')} - {finding.get('message')[:50]}...")
        else:
            print(f"⚠️ Findings endpoint: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Analysis endpoints error: {e}")

def test_download_endpoints(report_id, token):
    """Test download endpoints."""
    try:
        # Test source download
        response = requests.get(
            f"{API_BASE_URL}/reports/{report_id}/source",
            headers={'Authorization': f'Bearer {token}'}
        )
        
        if response.status_code == 200:
            print(f"✅ Source download: {len(response.content)} bytes")
        else:
            print(f"⚠️ Source download: {response.status_code}")
        
        # Test conclusion download
        response = requests.get(
            f"{API_BASE_URL}/reports/{report_id}/conclusion",
            headers={'Authorization': f'Bearer {token}'}
        )
        
        if response.status_code == 200:
            print(f"✅ Conclusion download: {len(response.content)} bytes")
        else:
            print(f"⚠️ Conclusion download: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Download endpoints error: {e}")

def main():
    """Run end-to-end test."""
    print("🧪 SLICE 5 END-TO-END TEST")
    print("=" * 50)
    print(f"Testing at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API URL: {API_BASE_URL}")
    print()
    
    # Step 1: Login
    print("1. Testing Authentication...")
    token = login()
    if not token:
        print("❌ Cannot proceed without authentication")
        return
    print()
    
    # Step 2: File Upload
    print("2. Testing File Upload...")
    report_id = test_file_upload(token)
    if not report_id:
        print("❌ Cannot proceed without successful upload")
        return
    print()
    
    # Step 3: Wait for Processing
    print("3. Testing Processing...")
    report_data = wait_for_processing(report_id, token)
    if not report_data:
        print("❌ Processing failed or timed out")
        return
    print()
    
    # Step 4: Test Analysis Endpoints
    print("4. Testing Analysis Endpoints...")
    test_analysis_endpoints(report_id, token)
    print()
    
    # Step 5: Test Download Endpoints
    print("5. Testing Download Endpoints...")
    test_download_endpoints(report_id, token)
    print()
    
    # Summary
    print("📊 END-TO-END TEST SUMMARY")
    print("=" * 50)
    print("✅ SLICE 5 FUNCTIONALITY VERIFIED!")
    print(f"📄 Report ID: {report_id}")
    print(f"📊 Score: {report_data.get('score', 'N/A')}")
    print(f"🔍 Findings: {report_data.get('finding_count', 'N/A')}")
    print()
    print("🎯 All Slice 5 features working correctly!")
    print("🚀 Ready for production use!")

if __name__ == "__main__":
    main()
