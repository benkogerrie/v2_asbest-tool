#!/usr/bin/env python3
"""
Test script om PUT requests te testen voor prompt updates
"""

import requests
import json

def test_put_requests():
    """Test PUT requests voor prompt updates"""
    base_url = "https://v2asbest-tool-production.up.railway.app"
    
    print("Testing PUT requests for prompt updates...")
    
    # Eerst een prompt aanmaken om te testen
    print("\n=== Step 1: Create test prompt ===")
    create_data = {
        "name": "test_put_prompt",
        "content": "Original content",
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
    
    # Test PUT request zonder trailing slash
    print(f"\n=== Step 2: Test PUT without trailing slash ===")
    update_data = {
        "content": "Updated content without slash",
        "status": "active"
    }
    
    url_without_slash = f"{base_url}/admin/prompts/{prompt_id}"
    print(f"URL: {url_without_slash}")
    
    try:
        response = requests.put(
            url_without_slash,
            json=update_data,
            timeout=10,
            allow_redirects=False  # Don't follow redirects
        )
        print(f"Status: {response.status_code}")
        print(f"Location header: {response.headers.get('Location', 'None')}")
        
        if response.status_code == 307:
            location = response.headers.get('Location', '')
            if location.startswith('http://'):
                print("❌ Redirects to HTTP - Mixed Content problem!")
            else:
                print("✅ Redirects to HTTPS")
        elif response.status_code == 200:
            print("✅ Direct success")
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test PUT request met trailing slash
    print(f"\n=== Step 3: Test PUT with trailing slash ===")
    update_data = {
        "content": "Updated content with slash",
        "status": "active"
    }
    
    url_with_slash = f"{base_url}/admin/prompts/{prompt_id}/"
    print(f"URL: {url_with_slash}")
    
    try:
        response = requests.put(
            url_with_slash,
            json=update_data,
            timeout=10,
            allow_redirects=False  # Don't follow redirects
        )
        print(f"Status: {response.status_code}")
        print(f"Location header: {response.headers.get('Location', 'None')}")
        
        if response.status_code == 200:
            print("✅ Direct success with trailing slash")
        elif response.status_code == 307:
            location = response.headers.get('Location', '')
            if location.startswith('http://'):
                print("❌ Still redirects to HTTP")
            else:
                print("✅ Redirects to HTTPS")
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Cleanup: Delete the test prompt
    print(f"\n=== Step 4: Cleanup ===")
    try:
        response = requests.delete(f"{base_url}/admin/prompts/{prompt_id}/")
        print(f"Delete Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Test prompt deleted")
        else:
            print(f"❌ Failed to delete: {response.text}")
    except Exception as e:
        print(f"❌ Error deleting: {e}")

if __name__ == "__main__":
    test_put_requests()
