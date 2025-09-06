#!/usr/bin/env python3
"""
Test script to check if the upload endpoint works in Slice 4.
"""
import requests
import json

# Railway API URL
API_BASE_URL = "https://v2asbest-tool-production.up.railway.app"

# Test credentials
TEST_EMAIL = "admin@bedrijfy.nl"
TEST_PASSWORD = "Admin123!"

def test_upload_endpoint():
    """Test if the upload endpoint works."""
    try:
        print(f"🔍 Testing upload endpoint...")
        
        # Login
        response = requests.post(
            f"{API_BASE_URL}/auth/jwt/login",
            data={
                "username": TEST_EMAIL,
                "password": TEST_PASSWORD
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code != 200:
            print(f"❌ Login failed: {response.status_code}")
            return
        
        token = response.json().get("access_token")
        print(f"✅ Login successful")
        
        # Test upload endpoint
        print(f"\n🔍 Testing upload endpoint...")
        
        # Create a dummy PDF file
        dummy_pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n174\n%%EOF"
        
        files = {
            'file': ('test_report.pdf', dummy_pdf_content, 'application/pdf')
        }
        
        response = requests.post(
            f"{API_BASE_URL}/reports/",
            headers={'Authorization': f'Bearer {token}'},
            files=files
        )
        
        print(f"   POST /reports/: {response.status_code}")
        
        if response.status_code == 401:
            print(f"      ❌ 401 Unauthorized - Upload endpoint failing")
            try:
                error_data = response.json()
                print(f"      Error: {json.dumps(error_data, indent=6)}")
            except:
                print(f"      Raw error: {response.text}")
        elif response.status_code in [200, 201]:
            print(f"      ✅ Success - Upload endpoint works!")
            try:
                response_data = response.json()
                print(f"      Response: {json.dumps(response_data, indent=6)}")
            except:
                print(f"      Raw response: {response.text}")
        else:
            print(f"      ⚠️ Unexpected status: {response.status_code}")
            try:
                error_data = response.json()
                print(f"      Error: {json.dumps(error_data, indent=6)}")
            except:
                print(f"      Raw error: {response.text}")
        
        # Test GET /reports endpoint
        print(f"\n🔍 Testing GET /reports endpoint...")
        
        response = requests.get(
            f"{API_BASE_URL}/reports/",
            headers={'Authorization': f'Bearer {token}'}
        )
        
        print(f"   GET /reports/: {response.status_code}")
        
        if response.status_code == 401:
            print(f"      ❌ 401 Unauthorized - GET reports endpoint failing")
            try:
                error_data = response.json()
                print(f"      Error: {json.dumps(error_data, indent=6)}")
            except:
                print(f"      Raw error: {response.text}")
        elif response.status_code in [200, 201]:
            print(f"      ✅ Success - GET reports endpoint works!")
            try:
                response_data = response.json()
                print(f"      Response: {json.dumps(response_data, indent=6)}")
            except:
                print(f"      Raw response: {response.text}")
        else:
            print(f"      ⚠️ Unexpected status: {response.status_code}")
            try:
                error_data = response.json()
                print(f"      Error: {json.dumps(error_data, indent=6)}")
            except:
                print(f"      Raw error: {response.text}")
        
    except Exception as e:
        print(f"❌ Exception: {e}")

def main():
    """Main function."""
    print("🔍 UPLOAD ENDPOINT TEST")
    print("=" * 30)
    
    test_upload_endpoint()
    
    print(f"\n📊 UPLOAD ENDPOINT SUMMARY")
    print("=" * 30)
    print("This test checks if the upload endpoint works in Slice 4")

if __name__ == "__main__":
    main()
