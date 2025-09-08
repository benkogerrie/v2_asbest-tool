#!/usr/bin/env python3
"""
Test script om POST endpoints te testen voor prompt actions
"""

import requests
import json

def test_post_endpoints():
    """Test POST endpoints voor prompt actions"""
    base_url = "https://v2asbest-tool-production.up.railway.app"
    
    print("Testing POST endpoints for prompt actions...")
    
    # Eerst een prompt aanmaken om te testen
    print("\n=== Step 1: Create test prompt ===")
    create_data = {
        "name": "test_post_prompt",
        "content": "Test content for POST endpoints",
        "version": 1,
        "status": "draft"
    }
    
    try:
        response = requests.post(
            f"{base_url}/admin/prompts/",
            json=create_data,
            timeout=10
        )
        print(f"Create Status: {response.status_code}")
        
        if response.status_code == 200:
            prompt_data = response.json()
            prompt_id = prompt_data["id"]
            print(f"✅ Created prompt with ID: {prompt_id}")
        else:
            print(f"❌ Failed to create prompt: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ Error creating prompt: {e}")
        return
    
    # Test activate endpoint
    print(f"\n=== Step 2: Test activate endpoint ===")
    
    # Test zonder trailing slash
    url_without_slash = f"{base_url}/admin/prompts/{prompt_id}/activate"
    print(f"URL without slash: {url_without_slash}")
    
    try:
        response = requests.post(
            url_without_slash,
            timeout=10,
            allow_redirects=False
        )
        print(f"Status: {response.status_code}")
        print(f"Location header: {response.headers.get('Location', 'None')}")
        
        if response.status_code == 307:
            location = response.headers.get('Location', '')
            if location.startswith('http://'):
                print("❌ Redirects to HTTP - Mixed Content problem!")
            else:
                print("✅ Redirects to HTTPS")
        elif response.status_code in [200, 422]:  # 422 might be expected without auth
            print("✅ Direct success or expected error")
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test met trailing slash
    url_with_slash = f"{base_url}/admin/prompts/{prompt_id}/activate/"
    print(f"URL with slash: {url_with_slash}")
    
    try:
        response = requests.post(
            url_with_slash,
            timeout=10,
            allow_redirects=False
        )
        print(f"Status: {response.status_code}")
        print(f"Location header: {response.headers.get('Location', 'None')}")
        
        if response.status_code == 307:
            location = response.headers.get('Location', '')
            if location.startswith('http://'):
                print("❌ Redirects to HTTP - Mixed Content problem!")
            else:
                print("✅ Redirects to HTTPS")
        elif response.status_code in [200, 422]:
            print("✅ Direct success or expected error")
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Cleanup: Delete the test prompt
    print(f"\n=== Step 3: Cleanup ===")
    try:
        response = requests.delete(f"{base_url}/admin/prompts/{prompt_id}")
        print(f"Delete Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Test prompt deleted")
        else:
            print(f"❌ Failed to delete: {response.text}")
    except Exception as e:
        print(f"❌ Error deleting: {e}")

if __name__ == "__main__":
    test_post_endpoints()
