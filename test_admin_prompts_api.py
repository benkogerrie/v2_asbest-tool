#!/usr/bin/env python3
"""
Test script voor Admin Prompts API endpoints
Test de nieuwe Slice 8 functionaliteit
"""

import requests
import json
import sys
from typing import Dict, Any

# Configuration
BASE_URL = "https://v21-asbest-tool-nutv.vercel.app"  # Production URL
# BASE_URL = "http://localhost:8000"  # Local URL

def make_request(method: str, endpoint: str, data: Dict[Any, Any] = None, headers: Dict[str, str] = None) -> Dict[Any, Any]:
    """Make HTTP request with error handling"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, timeout=30)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=30)
        elif method.upper() == "PUT":
            response = requests.put(url, json=data, headers=headers, timeout=30)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers, timeout=30)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        print(f"🔍 {method} {endpoint} -> {response.status_code}")
        
        if response.status_code >= 400:
            print(f"❌ Error: {response.text}")
            return {"error": response.text, "status_code": response.status_code}
        
        try:
            return response.json()
        except:
            return {"text": response.text, "status_code": response.status_code}
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return {"error": str(e)}

def test_health():
    """Test health endpoint"""
    print("\n🏥 Testing Health Endpoint...")
    result = make_request("GET", "/health")
    print(f"Health check: {result}")

def test_admin_prompts():
    """Test admin prompts endpoints"""
    print("\n🤖 Testing Admin Prompts Endpoints...")
    
    # Test 1: List prompts (should work without auth for now)
    print("\n1. Testing GET /admin/prompts")
    result = make_request("GET", "/admin/prompts")
    print(f"Prompts list: {result}")
    
    # Test 2: Create a test prompt
    print("\n2. Testing POST /admin/prompts")
    test_prompt = {
        "name": "test_prompt",
        "description": "Test prompt for API testing",
        "content": "This is a test prompt content for API validation.",
        "status": "draft"
    }
    result = make_request("POST", "/admin/prompts", test_prompt)
    print(f"Create prompt: {result}")
    
    if "id" in result:
        prompt_id = result["id"]
        
        # Test 3: Get specific prompt
        print(f"\n3. Testing GET /admin/prompts/{prompt_id}")
        result = make_request("GET", f"/admin/prompts/{prompt_id}")
        print(f"Get prompt: {result}")
        
        # Test 4: Test-run endpoint
        print(f"\n4. Testing POST /admin/prompts/{prompt_id}/test-run")
        test_run_data = {
            "sample_text": "Dit is een testdocument voor prompt validatie.",
            "checklist": "- Scope van onderzoek\n- Risicobeoordeling\n- Handtekening",
            "provider": "anthropic",
            "model": "claude-3-5-sonnet"
        }
        result = make_request("POST", f"/admin/prompts/{prompt_id}/test-run", test_run_data)
        print(f"Test run: {result}")
        
        # Test 5: Activate prompt
        print(f"\n5. Testing POST /admin/prompts/{prompt_id}/activate")
        result = make_request("POST", f"/admin/prompts/{prompt_id}/activate")
        print(f"Activate prompt: {result}")
        
        # Test 6: Archive prompt
        print(f"\n6. Testing POST /admin/prompts/{prompt_id}/archive")
        result = make_request("POST", f"/admin/prompts/{prompt_id}/archive")
        print(f"Archive prompt: {result}")
        
        # Test 7: Delete prompt
        print(f"\n7. Testing DELETE /admin/prompts/{prompt_id}")
        result = make_request("DELETE", f"/admin/prompts/{prompt_id}")
        print(f"Delete prompt: {result}")

def main():
    """Main test function"""
    print("🚀 Starting Admin Prompts API Tests")
    print(f"Testing against: {BASE_URL}")
    
    # Test health first
    test_health()
    
    # Test admin prompts
    test_admin_prompts()
    
    print("\n✅ API Tests Completed!")

if __name__ == "__main__":
    main()
