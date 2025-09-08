#!/usr/bin/env python3
"""
Test om te controleren of de description kolom daadwerkelijk bestaat in de database
"""

import requests
import json

def test_database_column():
    """Test of de description kolom bestaat door een prompt te maken en te bekijken"""
    base_url = "https://v2asbest-tool-production.up.railway.app"
    
    print("=== Testing Database Column Existence ===")
    
    # Test: Maak een prompt met description en kijk naar de response
    print("\n1. Creating prompt with description...")
    create_data = {
        "name": "column_test",
        "description": "Test description for column existence",
        "content": "Test content",
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
            
            # Check description
            description = prompt_data.get('description')
            print(f"   Description value: {repr(description)}")
            
            if description is None:
                print("   ❌ Description is None")
                print("   🔍 This suggests the database column does not exist")
                print("   🔍 OR the migration was not executed")
                print("   🔍 OR there's a problem with the ORM mapping")
            elif description == "":
                print("   ⚠️  Description is empty string")
                print("   🔍 Column exists but value is empty")
            else:
                print("   ✅ Description has value - column exists and works!")
            
            # Test update
            print(f"\n2. Testing description update...")
            update_data = {
                "description": "Updated description for column test"
            }
            
            update_response = requests.put(
                f"{base_url}/admin/prompts/{prompt_id}",
                json=update_data,
                timeout=10
            )
            print(f"   Update Status: {update_response.status_code}")
            
            if update_response.status_code == 200:
                updated_data = update_response.json()
                updated_description = updated_data.get('description')
                print(f"   Updated Description: {repr(updated_description)}")
                
                if updated_description == "Updated description for column test":
                    print("   ✅ Description update works - column exists!")
                else:
                    print("   ❌ Description update failed - column might not exist")
            else:
                print(f"   ❌ Update failed: {update_response.text}")
            
            # Cleanup
            delete_response = requests.delete(f"{base_url}/admin/prompts/{prompt_id}")
            print(f"\n3. Cleanup Status: {delete_response.status_code}")
            
        else:
            print(f"   ❌ Failed to create prompt: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "="*60)
    print("ANALYSE:")
    print("Als description altijd None is, dan is er een probleem met:")
    print("1. Database migratie niet uitgevoerd")
    print("2. ORM mapping niet correct")
    print("3. Database kolom bestaat niet")
    print("="*60)

if __name__ == "__main__":
    test_database_column()
