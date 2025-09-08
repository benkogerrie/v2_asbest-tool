#!/usr/bin/env python3
"""
Direct test om te controleren of de description kolom bestaat in de database
"""
import requests
import json

# Railway production URL
API_BASE_URL = "https://v2asbest-tool-production.up.railway.app"

def test_database_schema():
    """Test de database schema door een prompt te maken en te updaten"""
    print("🔍 Testing database schema directly...")
    
    try:
        # Maak een nieuwe prompt aan
        prompt_data = {
            "name": "Schema Test",
            "description": "Testing if description column exists",
            "content": "Test content",
            "status": "draft",
            "version": 1
        }
        
        print("📝 Creating new prompt...")
        response = requests.post(
            f"{API_BASE_URL}/admin/prompts",
            json=prompt_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            created_prompt = response.json()
            print(f"✅ Prompt created")
            print(f"   Response type: {type(created_prompt)}")
            print(f"   Response: {created_prompt}")
            
            # Handle both single object and list responses
            if isinstance(created_prompt, list):
                if len(created_prompt) > 0:
                    created_prompt = created_prompt[0]
                else:
                    print("❌ Empty list response")
                    return False
            
            print(f"   Name: {created_prompt.get('name')}")
            print(f"   ID: {created_prompt.get('id')}")
            print(f"   Description in response: {created_prompt.get('description')}")
            
            # Probeer de prompt te updaten met een description
            prompt_id = created_prompt.get('id')
            update_data = {
                "name": "Schema Test Updated",
                "description": "Updated description to test column",
                "content": "Updated content",
                "status": "active"
            }
            
            print(f"\n📝 Updating prompt {prompt_id}...")
            update_response = requests.put(
                f"{API_BASE_URL}/admin/prompts/{prompt_id}",
                json=update_data,
                headers={"Content-Type": "application/json"}
            )
            
            if update_response.status_code == 200:
                updated_prompt = update_response.json()
                print(f"✅ Prompt updated successfully")
                print(f"   Name: {updated_prompt.get('name')}")
                print(f"   Description: {updated_prompt.get('description')}")
                
                if updated_prompt.get('description') == update_data['description']:
                    print("  🎉 Description column exists and works!")
                    return True
                else:
                    print("  ⚠️  Description column may not exist or is not working")
                    return False
            else:
                print(f"❌ Update failed: {update_response.status_code}")
                print(f"   Response: {update_response.text}")
                return False
                
        else:
            print(f"❌ Creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing schema: {e}")
        return False

def check_migration_status():
    """Check of er migraties pending zijn"""
    print("\n🔍 Checking migration status...")
    
    try:
        # Probeer de health endpoint die migratie status zou moeten tonen
        response = requests.get(f"{API_BASE_URL}/healthz")
        
        if response.status_code == 200:
            print("✅ Health endpoint accessible")
            # De response zou migratie status kunnen bevatten
            print(f"   Response: {response.text[:200]}...")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error checking migration status: {e}")

if __name__ == "__main__":
    print("🚀 Direct database schema test...")
    print("=" * 50)
    
    # Test database schema
    schema_works = test_database_schema()
    
    # Check migration status
    check_migration_status()
    
    print("\n" + "=" * 50)
    print("📊 RESULT:")
    if schema_works:
        print("🎉 Description column exists and is working!")
    else:
        print("❌ Description column does not exist or is not working")
        print("   The migration may not have been applied yet")
