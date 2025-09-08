#!/usr/bin/env python3
"""
Test script voor rollback endpoint
"""
import requests
import json

# Railway production URL
API_BASE_URL = "https://v2asbest-tool-production.up.railway.app"

def test_rollback_endpoint():
    """Test de rollback endpoint direct"""
    print("🔍 Testing rollback endpoint...")
    
    try:
        # Eerst een prompt met meerdere versies vinden
        print("\n📝 Step 1: Finding prompts with multiple versions...")
        response = requests.get(f"{API_BASE_URL}/admin/prompts/")
        
        if response.status_code == 200:
            prompts = response.json()
            print(f"✅ Found {len(prompts)} total prompts")
            
            # Zoek naar prompts met dezelfde naam (versies)
            prompt_groups = {}
            for prompt in prompts:
                name = prompt.get('name')
                if name not in prompt_groups:
                    prompt_groups[name] = []
                prompt_groups[name].append(prompt)
            
            # Vind een prompt met meerdere versies
            multi_version_prompt = None
            for name, versions in prompt_groups.items():
                if len(versions) > 1:
                    multi_version_prompt = name
                    print(f"✅ Found prompt '{name}' with {len(versions)} versions")
                    for version in versions:
                        print(f"   - Version {version.get('version')}: {version.get('content')[:50]}...")
                    break
            
            if not multi_version_prompt:
                print("❌ No prompts with multiple versions found")
                return False
            
            # Test rollback
            print(f"\n📝 Step 2: Testing rollback for '{multi_version_prompt}'...")
            
            # Rollback naar versie 1
            rollback_data = {"target_version": 1}
            print(f"   Sending rollback data: {rollback_data}")
            
            rollback_response = requests.post(
                f"{API_BASE_URL}/admin/prompts/{multi_version_prompt}/rollback",
                json=rollback_data,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"   Response status: {rollback_response.status_code}")
            print(f"   Response headers: {dict(rollback_response.headers)}")
            
            if rollback_response.status_code == 200:
                rollback_result = rollback_response.json()
                print(f"✅ Rollback successful!")
                print(f"   New version: {rollback_result.get('version')}")
                print(f"   Content: {rollback_result.get('content')[:50]}...")
                return True
            else:
                print(f"❌ Rollback failed: {rollback_response.status_code}")
                print(f"   Response: {rollback_response.text}")
                return False
        else:
            print(f"❌ Failed to get prompts: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing rollback: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing rollback endpoint...")
    print("=" * 50)
    
    success = test_rollback_endpoint()
    
    print("\n" + "=" * 50)
    print("📊 RESULT:")
    if success:
        print("🎉 Rollback endpoint is working!")
    else:
        print("❌ Rollback endpoint has issues")
