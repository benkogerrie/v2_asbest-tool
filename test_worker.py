#!/usr/bin/env python3
"""
Test script to check worker service status.
"""
import requests
import json
import time

# Railway API URL
API_BASE_URL = "https://v2asbest-tool-production.up.railway.app"

# Test credentials
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

def test_redis_connection():
    """Test Redis connection via health endpoint."""
    try:
        response = requests.get(f"{API_BASE_URL}/healthz/storage", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Redis connection: {data.get('status', 'unknown')}")
            return True
        else:
            print(f"❌ Redis connection failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Redis connection error: {e}")
        return False

def test_simple_upload(token):
    """Test a simple file upload to see if worker processes it."""
    try:
        # Create a minimal PDF file
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
(Worker Test PDF) Tj
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
            'file': ('test_worker.pdf', test_pdf_content, 'application/pdf')
        }
        
        headers = {
            'Authorization': f'Bearer {token}'
        }
        
        response = requests.post(
            f"{API_BASE_URL}/reports/",
            files=files,
            headers=headers
        )
        
        print(f"Upload response: {response.status_code}")
        if response.status_code != 201:
            print(f"Upload error: {response.text}")
            return None
        
        data = response.json()
        report_id = data.get("id")
        print(f"✅ Simple upload successful: {report_id}")
        return report_id
        
    except Exception as e:
        print(f"❌ Simple upload error: {e}")
        return None

def check_report_status(report_id, token):
    """Check report status."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/reports/{report_id}",
            headers={'Authorization': f'Bearer {token}'}
        )
        
        if response.status_code == 200:
            data = response.json()
            status = data.get("status")
            print(f"Report status: {status}")
            return data
        else:
            print(f"Status check failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Status check error: {e}")
        return None

def main():
    """Main function."""
    print("🔧 WORKER SERVICE TEST")
    print("=" * 40)
    
    # Test 1: Login
    token = login()
    if not token:
        return
    
    # Test 2: Redis connection
    print("\n2. Testing Redis connection...")
    redis_ok = test_redis_connection()
    
    # Test 3: Simple upload
    print("\n3. Testing simple upload...")
    report_id = test_simple_upload(token)
    if not report_id:
        return
    
    # Test 4: Check status
    print("\n4. Checking report status...")
    time.sleep(2)  # Wait a bit
    report_data = check_report_status(report_id, token)
    
    if report_data:
        status = report_data.get("status")
        if status == "PROCESSING":
            print("⚠️ Report is still processing - worker might be slow")
        elif status == "DONE":
            print("✅ Worker processed the report successfully!")
        elif status == "FAILED":
            print("❌ Worker failed to process the report")
        else:
            print(f"ℹ️ Report status: {status}")
    
    print("\n📊 WORKER TEST SUMMARY")
    print("=" * 40)
    if redis_ok:
        print("✅ Redis connection: OK")
    else:
        print("❌ Redis connection: FAILED")
    
    if report_id:
        print("✅ File upload: OK")
    else:
        print("❌ File upload: FAILED")

if __name__ == "__main__":
    main()
