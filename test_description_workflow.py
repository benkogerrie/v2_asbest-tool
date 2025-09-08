#!/usr/bin/env python3
"""
Test script om te controleren of het description veld werkt
"""

import requests
import json

def test_description_workflow():
    """Test het volledige description workflow"""
    base_url = "https://v2asbest-tool-production.up.railway.app"
    
    print("=== Testing Description Field Workflow ===")
    
    # Test 1: Create prompt with description
    print("\n1. Creating prompt with description...")
    create_data = {
        "name": "test_description_workflow",
        "description": "Dit is een test beschrijving voor het workflow test",
        "content": "Test content voor description workflow",
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
            print(f"   Description in response: {prompt_data.get('description', 'NOT FOUND')}")
            
            if prompt_data.get('description'):
                print("   ✅ Description field works in creation!")
            else:
                print("   ❌ Description field not saved in creation")
                return
        else:
            print(f"   ❌ Failed to create prompt: {response.text}")
            return
            
    except Exception as e:
        print(f"   ❌ Error creating prompt: {e}")
        return
    
    # Test 2: Update prompt description
    print(f"\n2. Updating prompt description...")
    update_data = {
        "description": "Bijgewerkte beschrijving voor workflow test",
        "content": "Bijgewerkte content"
    }
    
    try:
        response = requests.put(
            f"{base_url}/admin/prompts/{prompt_id}",
            json=update_data,
            timeout=10
        )
        print(f"   Update Status: {response.status_code}")
        
        if response.status_code == 200:
            updated_data = response.json()
            print(f"   Updated Description: {updated_data.get('description', 'NOT FOUND')}")
            
            if updated_data.get('description') == "Bijgewerkte beschrijving voor workflow test":
                print("   ✅ Description field works in updates!")
            else:
                print("   ❌ Description field not saved in updates")
        else:
            print(f"   ❌ Failed to update prompt: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error updating prompt: {e}")
    
    # Test 3: Get prompts list to verify
    print(f"\n3. Getting prompts list to verify...")
    try:
        response = requests.get(f"{base_url}/admin/prompts/")
        print(f"   Get Status: {response.status_code}")
        
        if response.status_code == 200:
            prompts = response.json()
            test_prompt = next((p for p in prompts if p["id"] == prompt_id), None)
            
            if test_prompt:
                print(f"   Final Description: {test_prompt.get('description', 'NOT FOUND')}")
                if test_prompt.get('description') == "Bijgewerkte beschrijving voor workflow test":
                    print("   ✅ Description field persists correctly in list!")
                else:
                    print("   ❌ Description field not persisted in list")
            else:
                print("   ❌ Test prompt not found in list")
        else:
            print(f"   ❌ Failed to get prompts: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error getting prompts: {e}")
    
    # Test 4: Test with empty description
    print(f"\n4. Testing with empty description...")
    update_data = {
        "description": "",  # Empty description
        "content": "Content with empty description"
    }
    
    try:
        response = requests.put(
            f"{base_url}/admin/prompts/{prompt_id}",
            json=update_data,
            timeout=10
        )
        print(f"   Update Status: {response.status_code}")
        
        if response.status_code == 200:
            updated_data = response.json()
            print(f"   Empty Description: '{updated_data.get('description', 'NOT FOUND')}'")
            
            if updated_data.get('description') == "":
                print("   ✅ Empty description works!")
            else:
                print("   ❌ Empty description not handled correctly")
        else:
            print(f"   ❌ Failed to update with empty description: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error updating with empty description: {e}")
    
    # Cleanup: Delete the test prompt
    print(f"\n5. Cleanup...")
    try:
        response = requests.delete(f"{base_url}/admin/prompts/{prompt_id}")
        print(f"   Delete Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Test prompt deleted")
        else:
            print(f"   ❌ Failed to delete: {response.text}")
    except Exception as e:
        print(f"   ❌ Error deleting: {e}")
    
    print("\n" + "="*60)
    print("CONCLUSIE:")
    print("Als alle tests slagen, werkt het description veld correct.")
    print("Je kunt nu beschrijvingen toevoegen in de UI en ze worden opgeslagen.")
    print("="*60)

if __name__ == "__main__":
    test_description_workflow()
