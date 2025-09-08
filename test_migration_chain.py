#!/usr/bin/env python3
"""
Test om te controleren of de migratie chain correct is
"""

import requests
import json

def test_migration_chain():
    """Test of de migratie chain correct is door te kijken naar de database state"""
    base_url = "https://v2asbest-tool-production.up.railway.app"
    
    print("=== Testing Migration Chain ===")
    
    # Test: Maak een prompt en kijk naar alle velden
    print("\n1. Creating prompt and examining all fields...")
    create_data = {
        "name": "migration_chain_test",
        "description": "Test description for migration chain",
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
            
            # Examine all fields
            print(f"\n   All fields in response:")
            for key, value in prompt_data.items():
                print(f"     {key}: {repr(value)}")
            
            # Check if description field exists
            if 'description' in prompt_data:
                print(f"\n   ✅ Description field exists in response")
                if prompt_data['description'] is None:
                    print("   ❌ Description is None - database column does not exist")
                    print("   🔍 This means the migration was not executed")
                else:
                    print("   ✅ Description has value - migration worked!")
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
    print("CONCLUSIE:")
    print("Als description altijd None is, dan is de database migratie")
    print("niet uitgevoerd. Dit kan betekenen:")
    print("1. Railway heeft de migratie niet uitgevoerd")
    print("2. Er is een fout in de migratie")
    print("3. De migratie chain is gebroken")
    print("="*60)

if __name__ == "__main__":
    test_migration_chain()
