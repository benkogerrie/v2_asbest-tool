#!/usr/bin/env python3
"""
Test script voor admin endpoints
"""

import requests
import json

def test_admin_endpoints():
    """Test admin endpoints"""
    base_url = "https://v2asbest-tool-production.up.railway.app"
    
    print("🔍 Testing admin endpoints...")
    
    # Test 1: Health check
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/healthz", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Health check passed")
        else:
            print("   ❌ Health check failed")
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
    
    # Test 2: Admin prompts endpoint
    print("\n2. Testing admin prompts endpoint...")
    try:
        response = requests.get(f"{base_url}/admin/prompts", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Admin prompts endpoint accessible")
            data = response.json()
            print(f"   Response: {data}")
        elif response.status_code == 404:
            print("   ❌ Admin prompts endpoint not found (404)")
        else:
            print(f"   ⚠️  Unexpected status: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Admin prompts error: {e}")
    
    # Test 3: Try to create a test prompt
    print("\n3. Testing prompt creation...")
    try:
        test_prompt = {
            "name": "test_prompt",
            "description": "Test prompt for debugging",
            "content": "This is a test prompt content.",
            "status": "draft"
        }
        
        response = requests.post(
            f"{base_url}/admin/prompts",
            json=test_prompt,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200 or response.status_code == 201:
            print("   ✅ Prompt creation successful")
            data = response.json()
            print(f"   Response: {data}")
        else:
            print(f"   ❌ Prompt creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Prompt creation error: {e}")

if __name__ == "__main__":
    test_admin_endpoints()
