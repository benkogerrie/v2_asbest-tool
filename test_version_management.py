#!/usr/bin/env python3
"""
Test script om te controleren hoe versiebeheer van prompts werkt
"""
import requests
import json

# Railway production URL
API_BASE_URL = "https://v2asbest-tool-production.up.railway.app"

def test_version_management():
    """Test hoe versiebeheer werkt bij prompts"""
    print("🔍 Testing prompt version management...")
    
    try:
        # Test 1: Maak een prompt aan met versie 1
        print("\n📝 Test 1: Creating prompt with version 1...")
        prompt_v1 = {
            "name": "Version Test Prompt",
            "description": "Testing version management",
            "content": "This is version 1 of the prompt",
            "status": "draft",
            "version": 1
        }
        
        response_v1 = requests.post(
            f"{API_BASE_URL}/admin/prompts",
            json=prompt_v1,
            headers={"Content-Type": "application/json"}
        )
        
        if response_v1.status_code == 200:
            result_v1 = response_v1.json()
            if isinstance(result_v1, list) and len(result_v1) > 0:
                created_v1 = result_v1[0]
            else:
                created_v1 = result_v1
            
            print(f"✅ Version 1 created: ID {created_v1.get('id')}")
            print(f"   Name: {created_v1.get('name')}")
            print(f"   Version: {created_v1.get('version')}")
            print(f"   Content: {created_v1.get('content')}")
            
            # Test 2: Probeer dezelfde prompt met versie 2 aan te maken
            print(f"\n📝 Test 2: Creating same prompt with version 2...")
            prompt_v2 = {
                "name": "Version Test Prompt",  # Zelfde naam
                "description": "Testing version management",
                "content": "This is version 2 of the prompt",
                "status": "draft",
                "version": 2
            }
            
            response_v2 = requests.post(
                f"{API_BASE_URL}/admin/prompts",
                json=prompt_v2,
                headers={"Content-Type": "application/json"}
            )
            
            if response_v2.status_code == 200:
                result_v2 = response_v2.json()
                if isinstance(result_v2, list) and len(result_v2) > 0:
                    created_v2 = result_v2[0]
                else:
                    created_v2 = result_v2
                
                print(f"✅ Version 2 created: ID {created_v2.get('id')}")
                print(f"   Name: {created_v2.get('name')}")
                print(f"   Version: {created_v2.get('version')}")
                print(f"   Content: {created_v2.get('content')}")
                
                # Test 3: Haal alle prompts op om te zien of beide versies bestaan
                print(f"\n📝 Test 3: Checking if both versions exist...")
                all_response = requests.get(f"{API_BASE_URL}/admin/prompts/")
                
                if all_response.status_code == 200:
                    all_prompts = all_response.json()
                    print(f"✅ Retrieved {len(all_prompts)} total prompts")
                    
                    # Zoek naar onze test prompts
                    version_test_prompts = []
                    for prompt in all_prompts:
                        if prompt.get('name') == 'Version Test Prompt':
                            version_test_prompts.append(prompt)
                    
                    print(f"   Found {len(version_test_prompts)} 'Version Test Prompt' entries:")
                    for prompt in version_test_prompts:
                        print(f"     - Version {prompt.get('version')}: {prompt.get('content')}")
                    
                    if len(version_test_prompts) == 2:
                        print("   🎉 Both versions are preserved!")
                        return True
                    else:
                        print("   ⚠️  Not all versions are preserved")
                        return False
                else:
                    print(f"❌ Failed to get all prompts: {all_response.status_code}")
                    return False
            else:
                print(f"❌ Version 2 creation failed: {response_v2.status_code}")
                print(f"   Response: {response_v2.text}")
                return False
        else:
            print(f"❌ Version 1 creation failed: {response_v1.status_code}")
            print(f"   Response: {response_v1.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing version management: {e}")
        return False

def test_update_version():
    """Test wat er gebeurt als je de versie van een bestaande prompt update"""
    print("\n🔍 Testing version update behavior...")
    
    try:
        # Haal een bestaande prompt op
        response = requests.get(f"{API_BASE_URL}/admin/prompts/")
        
        if response.status_code == 200:
            prompts = response.json()
            if len(prompts) > 0:
                existing_prompt = prompts[0]
                prompt_id = existing_prompt.get('id')
                current_version = existing_prompt.get('version')
                
                print(f"   Testing with prompt: {existing_prompt.get('name')} (v{current_version})")
                
                # Probeer de versie te updaten
                update_data = {
                    "name": existing_prompt.get('name'),
                    "description": existing_prompt.get('description'),
                    "content": existing_prompt.get('content'),
                    "version": current_version + 1,  # Verhoog versie
                    "status": existing_prompt.get('status')
                }
                
                update_response = requests.put(
                    f"{API_BASE_URL}/admin/prompts/{prompt_id}",
                    json=update_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if update_response.status_code == 200:
                    updated_prompt = update_response.json()
                    print(f"   ✅ Update successful")
                    print(f"   New version: {updated_prompt.get('version')}")
                    print(f"   Expected: {current_version + 1}")
                    
                    if updated_prompt.get('version') == current_version + 1:
                        print("   🎉 Version was updated successfully!")
                        return True
                    else:
                        print("   ❌ Version was not updated")
                        return False
                else:
                    print(f"   ❌ Update failed: {update_response.status_code}")
                    print(f"   Response: {update_response.text}")
                    return False
            else:
                print("   ❌ No prompts found to test")
                return False
        else:
            print(f"❌ Failed to get prompts: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing version update: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing prompt version management...")
    print("=" * 60)
    
    # Test 1: Versiebeheer bij aanmaken
    version_management_works = test_version_management()
    
    # Test 2: Versie update gedrag
    version_update_works = test_update_version()
    
    print("\n" + "=" * 60)
    print("📊 VERSION MANAGEMENT RESULTS:")
    print(f"  Multiple versions preserved: {'✅' if version_management_works else '❌'}")
    print(f"  Version updates work: {'✅' if version_update_works else '❌'}")
    
    if version_management_works:
        print("\n🎉 Version management is working correctly!")
        print("   - Multiple versions of the same prompt can coexist")
        print("   - Each version is stored separately in the database")
    else:
        print("\n⚠️  Version management may not be working as expected")
        print("   - Check if the UniqueConstraint is properly enforced")
        print("   - Verify that updates don't overwrite existing versions")
