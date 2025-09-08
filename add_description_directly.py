#!/usr/bin/env python3
"""
Direct SQL approach om description kolom toe te voegen
"""

import requests
import json

def test_direct_sql_approach():
    """Test of we de description kolom kunnen toevoegen via een API call"""
    base_url = "https://v2asbest-tool-production.up.railway.app"
    
    print("=== Direct SQL Approach Test ===")
    
    # Test: Maak een prompt met alleen de verplichte velden
    print("\n1. Testing with minimal required fields...")
    create_data = {
        "name": "direct_sql_test",
        "content": "Test content for direct SQL",
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
            
            # Check if description field exists in response
            if 'description' in prompt_data:
                print(f"   ✅ Description field exists: {repr(prompt_data['description'])}")
            else:
                print("   ❌ Description field missing from response")
            
            # Try to update with description
            print(f"\n2. Testing update with description...")
            update_data = {
                "description": "Direct SQL test description"
            }
            
            update_response = requests.put(
                f"{base_url}/admin/prompts/{prompt_id}",
                json=update_data,
                timeout=10
            )
            print(f"   Update Status: {update_response.status_code}")
            
            if update_response.status_code == 200:
                updated_data = update_response.json()
                if 'description' in updated_data:
                    print(f"   Updated Description: {repr(updated_data['description'])}")
                else:
                    print("   ❌ Description field missing from update response")
            
            # Cleanup
            delete_response = requests.delete(f"{base_url}/admin/prompts/{prompt_id}")
            print(f"\n3. Cleanup Status: {delete_response.status_code}")
            
        else:
            print(f"   ❌ Failed to create prompt: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_direct_sql_approach()
