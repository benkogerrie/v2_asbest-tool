#!/usr/bin/env python3
"""
Test script om te controleren of de description kolom echt bestaat in de database
"""
import requests
import json

# Railway production URL
API_BASE_URL = "https://v2asbest-tool-production.up.railway.app"

def test_database_schema_via_api():
    """Test de database schema door verschillende API calls"""
    print("🔍 Testing database schema via API...")
    
    try:
        # Test 1: Maak een prompt aan met description
        print("\n📝 Test 1: Creating prompt with description...")
        prompt_data = {
            "name": "Database Column Test",
            "description": "Testing if description column exists in database",
            "content": "Test content for database column verification",
            "status": "draft",
            "version": 1
        }
        
        create_response = requests.post(
            f"{API_BASE_URL}/admin/prompts",
            json=prompt_data,
            headers={"Content-Type": "application/json"}
        )
        
        if create_response.status_code == 200:
            created_result = create_response.json()
            print(f"✅ Prompt creation successful")
            
            # Handle list response
            if isinstance(created_result, list) and len(created_result) > 0:
                created_prompt = created_result[0]
            else:
                created_prompt = created_result
            
            print(f"   Created prompt ID: {created_prompt.get('id')}")
            print(f"   Description in response: {created_prompt.get('description')}")
            print(f"   Expected description: {prompt_data['description']}")
            
            # Test 2: Haal de prompt opnieuw op via GET
            print(f"\n📝 Test 2: Retrieving prompt via GET...")
            prompt_id = created_prompt.get('id')
            
            get_response = requests.get(f"{API_BASE_URL}/admin/prompts/{prompt_id}")
            
            if get_response.status_code == 200:
                retrieved_prompt = get_response.json()
                print(f"✅ Prompt retrieval successful")
                print(f"   Retrieved description: {retrieved_prompt.get('description')}")
                print(f"   Expected description: {prompt_data['description']}")
                
                # Test 3: Update de prompt met een nieuwe description
                print(f"\n📝 Test 3: Updating prompt description...")
                update_data = {
                    "name": "Database Column Test",
                    "description": "Updated description to test column persistence",
                    "content": "Test content for database column verification",
                    "status": "draft"
                }
                
                update_response = requests.put(
                    f"{API_BASE_URL}/admin/prompts/{prompt_id}",
                    json=update_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if update_response.status_code == 200:
                    updated_prompt = update_response.json()
                    print(f"✅ Prompt update successful")
                    print(f"   Updated description: {updated_prompt.get('description')}")
                    print(f"   Expected description: {update_data['description']}")
                    
                    # Test 4: Haal alle prompts op om te zien of de description persistent is
                    print(f"\n📝 Test 4: Checking all prompts for description persistence...")
                    all_response = requests.get(f"{API_BASE_URL}/admin/prompts/")
                    
                    if all_response.status_code == 200:
                        all_prompts = all_response.json()
                        print(f"✅ Retrieved {len(all_prompts)} prompts")
                        
                        # Zoek onze test prompt
                        test_prompt = None
                        for prompt in all_prompts:
                            if prompt.get('id') == prompt_id:
                                test_prompt = prompt
                                break
                        
                        if test_prompt:
                            print(f"   Found test prompt: {test_prompt.get('name')}")
                            print(f"   Description in list: {test_prompt.get('description')}")
                            print(f"   Expected: {update_data['description']}")
                            
                            if test_prompt.get('description') == update_data['description']:
                                print("   🎉 Description column is working correctly!")
                                return True
                            else:
                                print("   ❌ Description not persistent in list view")
                                return False
                        else:
                            print("   ❌ Test prompt not found in list")
                            return False
                    else:
                        print(f"❌ Failed to get all prompts: {all_response.status_code}")
                        return False
                else:
                    print(f"❌ Prompt update failed: {update_response.status_code}")
                    print(f"   Response: {update_response.text}")
                    return False
            else:
                print(f"❌ Prompt retrieval failed: {get_response.status_code}")
                return False
        else:
            print(f"❌ Prompt creation failed: {create_response.status_code}")
            print(f"   Response: {create_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing database schema: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing database column existence and functionality...")
    print("=" * 60)
    
    # Test database schema
    column_works = test_database_schema_via_api()
    
    print("\n" + "=" * 60)
    print("📊 RESULT:")
    if column_works:
        print("🎉 Description column exists and is fully functional!")
    else:
        print("❌ Description column does not exist or is not working")
        print("   The database migration may not have been applied")
