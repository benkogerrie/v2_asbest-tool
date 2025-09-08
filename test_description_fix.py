#!/usr/bin/env python3
"""
Test script om te controleren of de description fix werkt
"""
import requests
import json

# Railway production URL
API_BASE_URL = "https://v2asbest-tool-production.up.railway.app"

def test_existing_prompts():
    """Test of bestaande prompts nu description hebben"""
    print("🔍 Testing existing prompts for description field...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/admin/prompts/")
        
        if response.status_code == 200:
            prompts = response.json()
            print(f"✅ Found {len(prompts)} prompts")
            
            for i, prompt in enumerate(prompts):
                print(f"  Prompt {i+1}: '{prompt.get('name')}'")
                print(f"    Description: {prompt.get('description')}")
                print(f"    All fields: {list(prompt.keys())}")
                
                if prompt.get('description') is not None:
                    print(f"    🎉 This prompt has a non-null description!")
                    return True
            
            print("  ⚠️  All descriptions are still null")
            return False
        else:
            print(f"❌ Failed to get prompts: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_create_new_prompt():
    """Test het aanmaken van een nieuwe prompt met description"""
    print("\n🔍 Testing creation of new prompt with description...")
    
    try:
        prompt_data = {
            "name": "Description Test Fix",
            "description": "This should work now after the API fix",
            "content": "Test content for description fix",
            "status": "draft",
            "version": 1
        }
        
        response = requests.post(
            f"{API_BASE_URL}/admin/prompts",
            json=prompt_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Prompt creation successful")
            
            # Handle list response
            if isinstance(result, list) and len(result) > 0:
                created_prompt = result[0]
            else:
                created_prompt = result
            
            print(f"   Created prompt: {created_prompt.get('name')}")
            print(f"   Description: {created_prompt.get('description')}")
            print(f"   Expected: {prompt_data['description']}")
            
            if created_prompt.get('description') == prompt_data['description']:
                print("   🎉 Description is correctly saved and returned!")
                return True
            else:
                print("   ❌ Description was not saved correctly")
                return False
        else:
            print(f"❌ Prompt creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_update_existing_prompt():
    """Test het updaten van een bestaande prompt met description"""
    print("\n🔍 Testing update of existing prompt with description...")
    
    try:
        # Eerst een bestaande prompt ophalen
        response = requests.get(f"{API_BASE_URL}/admin/prompts/")
        
        if response.status_code == 200:
            prompts = response.json()
            if len(prompts) > 0:
                existing_prompt = prompts[0]
                prompt_id = existing_prompt.get('id')
                
                print(f"   Updating prompt: {existing_prompt.get('name')} (ID: {prompt_id})")
                
                # Update data
                update_data = {
                    "name": existing_prompt.get('name'),
                    "description": "Updated description via API fix test",
                    "content": existing_prompt.get('content'),
                    "status": existing_prompt.get('status')
                }
                
                # Update request
                update_response = requests.put(
                    f"{API_BASE_URL}/admin/prompts/{prompt_id}",
                    json=update_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if update_response.status_code == 200:
                    updated_prompt = update_response.json()
                    print(f"   ✅ Update successful")
                    print(f"   Description: {updated_prompt.get('description')}")
                    print(f"   Expected: {update_data['description']}")
                    
                    if updated_prompt.get('description') == update_data['description']:
                        print("   🎉 Description update works correctly!")
                        return True
                    else:
                        print("   ❌ Description update failed")
                        return False
                else:
                    print(f"   ❌ Update failed: {update_response.status_code}")
                    print(f"   Response: {update_response.text}")
                    return False
            else:
                print("   ❌ No prompts found to update")
                return False
        else:
            print(f"❌ Failed to get prompts for update: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing description field fix...")
    print("=" * 50)
    
    # Test 1: Check existing prompts
    existing_works = test_existing_prompts()
    
    # Test 2: Create new prompt
    creation_works = test_create_new_prompt()
    
    # Test 3: Update existing prompt
    update_works = test_update_existing_prompt()
    
    print("\n" + "=" * 50)
    print("📊 RESULTS:")
    print(f"  Existing prompts: {'✅' if existing_works else '❌'}")
    print(f"  New prompt creation: {'✅' if creation_works else '❌'}")
    print(f"  Prompt update: {'✅' if update_works else '❌'}")
    
    if creation_works or update_works:
        print("\n🎉 Description field is working!")
    else:
        print("\n❌ Description field is still not working")
