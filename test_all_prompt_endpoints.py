#!/usr/bin/env python3
"""
Test script om alle prompt endpoints te testen
"""

import requests
import json

def test_all_prompt_endpoints():
    """Test alle prompt endpoints"""
    base_url = "https://v2asbest-tool-production.up.railway.app"
    
    print("Testing all prompt endpoints...")
    
    # Eerst een prompt aanmaken om te testen
    print("\n=== Step 1: Create test prompt ===")
    create_data = {
        "name": "test_all_endpoints",
        "content": "Test content for all endpoints",
        "version": 1,
        "status": "draft"
    }
    
    try:
        response = requests.post(
            f"{base_url}/admin/prompts/",  # POST creation needs trailing slash
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
    
    # Test alle endpoints
    endpoints_to_test = [
        (f"/admin/prompts/{prompt_id}", "PUT", "Update prompt"),
        (f"/admin/prompts/{prompt_id}/activate", "POST", "Activate prompt"),
        (f"/admin/prompts/{prompt_id}/archive", "POST", "Archive prompt"),
        (f"/admin/prompts/{prompt_id}/test-run", "POST", "Test prompt"),
        (f"/admin/prompts/{prompt_id}", "DELETE", "Delete prompt"),
    ]
    
    for endpoint, method, description in endpoints_to_test:
        print(f"\n=== {description} ===")
        url = base_url + endpoint
        print(f"URL: {url}")
        print(f"Method: {method}")
        
        try:
            if method == "PUT":
                response = requests.put(
                    url,
                    json={"content": "Updated content"},
                    timeout=10,
                    allow_redirects=False
                )
            elif method == "POST":
                if "test-run" in endpoint:
                    response = requests.post(
                        url,
                        json={"sample_text": "Test"},
                        timeout=10,
                        allow_redirects=False
                    )
                else:
                    response = requests.post(
                        url,
                        timeout=10,
                        allow_redirects=False
                    )
            elif method == "DELETE":
                response = requests.delete(
                    url,
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
    
    print("\n" + "="*60)
    print("SUMMARY:")
    print("All endpoints should work without trailing slashes")
    print("to avoid HTTP redirects that cause Mixed Content errors.")
    print("="*60)

if __name__ == "__main__":
    test_all_prompt_endpoints()
