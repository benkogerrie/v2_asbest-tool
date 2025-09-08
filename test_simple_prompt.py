#!/usr/bin/env python3
"""
Eenvoudige test om te controleren of de prompts API werkt
"""

import requests
import json

def test_simple_prompt():
    """Test eenvoudige prompt creation zonder description"""
    base_url = "https://v2asbest-tool-production.up.railway.app"
    
    print("=== Simple Prompt Test ===")
    
    # Test 1: Get prompts list
    print("\n1. Getting prompts list...")
    try:
        response = requests.get(f"{base_url}/admin/prompts/")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            prompts = response.json()
            print(f"   ✅ Found {len(prompts)} prompts")
            if prompts:
                first_prompt = prompts[0]
                print(f"   First prompt: {first_prompt.get('name', 'Unknown')}")
                print(f"   Has description field: {'description' in first_prompt}")
                if 'description' in first_prompt:
                    print(f"   Description value: {first_prompt.get('description')}")
        else:
            print(f"   ❌ Failed: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Create simple prompt without description
    print("\n2. Creating simple prompt...")
    create_data = {
        "name": "simple_test",
        "content": "Simple test content",
        "version": 1,
        "status": "draft"
    }
    
    try:
        response = requests.post(
            f"{base_url}/admin/prompts/",
            json=create_data,
            timeout=10
        )
        print(f"   Create Status: {response.status_code}")
        
        if response.status_code == 200:
            prompt_data = response.json()
            prompt_id = prompt_data["id"]
            print(f"   ✅ Created prompt with ID: {prompt_id}")
            print(f"   Response fields: {list(prompt_data.keys())}")
            
            # Cleanup
            delete_response = requests.delete(f"{base_url}/admin/prompts/{prompt_id}")
            print(f"   Cleanup Status: {delete_response.status_code}")
        else:
            print(f"   ❌ Failed: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_simple_prompt()
