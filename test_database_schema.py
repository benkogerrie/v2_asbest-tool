#!/usr/bin/env python3
"""
Test om te controleren of de database schema correct is
"""

import requests
import json

def test_database_schema():
    """Test database schema door een prompt te maken en te bekijken"""
    base_url = "https://v2asbest-tool-production.up.railway.app"
    
    print("=== Testing Database Schema ===")
    
    # Test: Create prompt and examine response
    print("\n1. Creating prompt and examining response...")
    create_data = {
        "name": "schema_test",
        "description": "Schema test description",
        "content": "Schema test content",
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
            
            # Examine all fields
            print(f"\n   Response fields and values:")
            for key, value in prompt_data.items():
                print(f"     {key}: {value} (type: {type(value).__name__})")
            
            # Check if description field exists and its value
            if 'description' in prompt_data:
                print(f"\n   ✅ Description field exists in response")
                print(f"   Description value: {repr(prompt_data['description'])}")
                
                if prompt_data['description'] is None:
                    print("   ❌ Description is None - database column might not exist")
                elif prompt_data['description'] == "":
                    print("   ⚠️  Description is empty string - might be working but empty")
                else:
                    print("   ✅ Description has a value - working correctly!")
            else:
                print("   ❌ Description field missing from response")
            
            # Cleanup
            delete_response = requests.delete(f"{base_url}/admin/prompts/{prompt_id}")
            print(f"\n   Cleanup Status: {delete_response.status_code}")
            
        else:
            print(f"   ❌ Failed to create prompt: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "="*60)
    print("ANALYSE:")
    print("Als description altijd None is, dan is de database migratie")
    print("nog niet uitgevoerd op Railway.")
    print("="*60)

if __name__ == "__main__":
    test_database_schema()
