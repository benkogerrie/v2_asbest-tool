#!/usr/bin/env python3
"""
Test om te controleren of description daadwerkelijk kan worden opgeslagen
"""

import requests
import json

def test_description_save():
    """Test description save functionality"""
    base_url = "https://v2asbest-tool-production.up.railway.app"
    
    print("=== Testing Description Save ===")
    
    # Test 1: Create prompt with description
    print("\n1. Creating prompt with description...")
    create_data = {
        "name": "test_description_save",
        "description": "Dit is een test beschrijving die opgeslagen moet worden",
        "content": "Test content met beschrijving",
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
            print(f"   Description in response: '{prompt_data.get('description', 'NOT FOUND')}'")
            
            if prompt_data.get('description') == "Dit is een test beschrijving die opgeslagen moet worden":
                print("   ✅ Description field works in creation!")
            else:
                print("   ❌ Description field not saved in creation")
                print(f"   Expected: 'Dit is een test beschrijving die opgeslagen moet worden'")
                print(f"   Got: '{prompt_data.get('description')}'")
        else:
            print(f"   ❌ Failed to create prompt: {response.text}")
            return
            
    except Exception as e:
        print(f"   ❌ Error creating prompt: {e}")
        return
    
    # Test 2: Update description
    print(f"\n2. Updating description...")
    update_data = {
        "description": "Bijgewerkte beschrijving voor save test"
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
            print(f"   Updated Description: '{updated_data.get('description', 'NOT FOUND')}'")
            
            if updated_data.get('description') == "Bijgewerkte beschrijving voor save test":
                print("   ✅ Description field works in updates!")
            else:
                print("   ❌ Description field not saved in updates")
        else:
            print(f"   ❌ Failed to update prompt: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error updating prompt: {e}")
    
    # Test 3: Verify in list
    print(f"\n3. Verifying in prompts list...")
    try:
        response = requests.get(f"{base_url}/admin/prompts/")
        print(f"   Get Status: {response.status_code}")
        
        if response.status_code == 200:
            prompts = response.json()
            test_prompt = next((p for p in prompts if p["id"] == prompt_id), None)
            
            if test_prompt:
                print(f"   Description in list: '{test_prompt.get('description', 'NOT FOUND')}'")
                if test_prompt.get('description') == "Bijgewerkte beschrijving voor save test":
                    print("   ✅ Description field persists in list!")
                else:
                    print("   ❌ Description field not persisted in list")
            else:
                print("   ❌ Test prompt not found in list")
        else:
            print(f"   ❌ Failed to get prompts: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error getting prompts: {e}")
    
    # Cleanup
    print(f"\n4. Cleanup...")
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
    print("Als alle tests slagen, werkt het description veld volledig!")
    print("Je kunt nu beschrijvingen toevoegen in de UI.")
    print("="*60)

if __name__ == "__main__":
    test_description_save()
