#!/usr/bin/env python3
"""
Test om te controleren of de migratie status
"""

import requests
import json

def test_migration_status():
    """Test om te controleren of de migratie is uitgevoerd"""
    base_url = "https://v2asbest-tool-production.up.railway.app"
    
    print("=== Testing Migration Status ===")
    
    # Test: Probeer een prompt te maken met description en kijk naar de response
    print("\n1. Testing prompt creation with description...")
    create_data = {
        "name": "migration_test",
        "description": "Test description for migration",
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
                print("   ❌ Description is None - migration not executed")
                print("   🔍 This means the database column 'description' does not exist")
            elif description == "":
                print("   ⚠️  Description is empty string - migration executed but value not saved")
            else:
                print("   ✅ Description has value - migration working!")
            
            # Cleanup
            delete_response = requests.delete(f"{base_url}/admin/prompts/{prompt_id}")
            print(f"   Cleanup Status: {delete_response.status_code}")
            
        else:
            print(f"   ❌ Failed to create prompt: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "="*60)
    print("CONCLUSIE:")
    print("Als description altijd None is, dan is de database migratie")
    print("nog niet uitgevoerd op Railway. Dit kan betekenen:")
    print("1. Railway heeft de migratie nog niet uitgevoerd")
    print("2. Er is een probleem met de migratie")
    print("3. Railway voert migraties niet automatisch uit")
    print("="*60)

if __name__ == "__main__":
    test_migration_status()
