#!/usr/bin/env python3
"""
Test script voor het nieuwe versiebeheer systeem
"""
import requests
import json

# Railway production URL
API_BASE_URL = "https://v2asbest-tool-production.up.railway.app"

def test_automatic_versioning():
    """Test automatische versieverhoging"""
    print("🔍 Testing automatic versioning...")
    
    try:
        # Test 1: Maak een nieuwe prompt aan
        print("\n📝 Test 1: Creating new prompt...")
        prompt_data = {
            "name": "Version Test System",
            "description": "Testing automatic versioning system",
            "content": "This is the initial version of the prompt",
            "status": "draft"
        }
        
        response = requests.post(
            f"{API_BASE_URL}/admin/prompts",
            json=prompt_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            created_prompt = response.json()
            print(f"✅ Prompt created successfully")
            print(f"   Name: {created_prompt.get('name')}")
            print(f"   Version: {created_prompt.get('version')}")
            print(f"   Content: {created_prompt.get('content')}")
            
            # Test 2: Update de prompt (zou nieuwe versie moeten maken)
            print(f"\n📝 Test 2: Updating prompt (should create new version)...")
            update_data = {
                "name": "Version Test System",
                "description": "Updated description for version 2",
                "content": "This is the updated version of the prompt",
                "status": "active"
            }
            
            update_response = requests.put(
                f"{API_BASE_URL}/admin/prompts/{created_prompt.get('id')}",
                json=update_data,
                headers={"Content-Type": "application/json"}
            )
            
            if update_response.status_code == 200:
                updated_prompt = update_response.json()
                print(f"✅ Prompt updated successfully")
                print(f"   New ID: {updated_prompt.get('id')}")
                print(f"   New Version: {updated_prompt.get('version')}")
                print(f"   New Content: {updated_prompt.get('content')}")
                
                # Check if it's a new version
                if updated_prompt.get('version') > created_prompt.get('version'):
                    print("   🎉 New version created automatically!")
                    return True, created_prompt.get('name')
                else:
                    print("   ❌ Version was not incremented")
                    return False, None
            else:
                print(f"❌ Update failed: {update_response.status_code}")
                print(f"   Response: {update_response.text}")
                return False, None
        else:
            print(f"❌ Creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ Error in automatic versioning test: {e}")
        return False, None

def test_version_history_api(prompt_name):
    """Test versiegeschiedenis API"""
    print(f"\n🔍 Testing version history API for '{prompt_name}'...")
    
    try:
        # Test 1: Haal alle versies op
        print(f"\n📝 Test 1: Getting all versions...")
        response = requests.get(f"{API_BASE_URL}/admin/prompts/{prompt_name}/versions")
        
        if response.status_code == 200:
            versions = response.json()
            print(f"✅ Retrieved {len(versions)} versions")
            
            for i, version in enumerate(versions):
                print(f"   Version {version.get('version')}: {version.get('content')[:50]}...")
                print(f"     Status: {version.get('status')}")
                print(f"     Created: {version.get('created_at')}")
            
            if len(versions) >= 2:
                print("   🎉 Multiple versions found!")
                
                # Test 2: Haal specifieke versie op
                print(f"\n📝 Test 2: Getting specific version...")
                specific_version = versions[1]  # Second version
                version_num = specific_version.get('version')
                
                specific_response = requests.get(f"{API_BASE_URL}/admin/prompts/{prompt_name}/versions/{version_num}")
                
                if specific_response.status_code == 200:
                    specific_prompt = specific_response.json()
                    print(f"✅ Retrieved specific version {version_num}")
                    print(f"   Content: {specific_prompt.get('content')[:50]}...")
                    return True
                else:
                    print(f"❌ Failed to get specific version: {specific_response.status_code}")
                    return False
            else:
                print("   ⚠️  Not enough versions for full test")
                return False
        else:
            print(f"❌ Failed to get versions: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error in version history test: {e}")
        return False

def test_rollback_functionality(prompt_name):
    """Test rollback functionaliteit"""
    print(f"\n🔍 Testing rollback functionality for '{prompt_name}'...")
    
    try:
        # Haal alle versies op om een target versie te vinden
        response = requests.get(f"{API_BASE_URL}/admin/prompts/{prompt_name}/versions")
        
        if response.status_code == 200:
            versions = response.json()
            
            if len(versions) >= 2:
                # Rollback naar de tweede versie
                target_version = versions[1].get('version')
                print(f"\n📝 Rolling back to version {target_version}...")
                
                rollback_data = {"target_version": target_version}
                rollback_response = requests.post(
                    f"{API_BASE_URL}/admin/prompts/{prompt_name}/rollback",
                    json=rollback_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if rollback_response.status_code == 200:
                    rollback_prompt = rollback_response.json()
                    print(f"✅ Rollback successful")
                    print(f"   New version: {rollback_prompt.get('version')}")
                    print(f"   Content: {rollback_prompt.get('content')[:50]}...")
                    
                    # Check if content matches target version
                    if rollback_prompt.get('content') == versions[1].get('content'):
                        print("   🎉 Rollback content matches target version!")
                        return True
                    else:
                        print("   ❌ Rollback content doesn't match target")
                        return False
                else:
                    print(f"❌ Rollback failed: {rollback_response.status_code}")
                    print(f"   Response: {rollback_response.text}")
                    return False
            else:
                print("   ⚠️  Not enough versions for rollback test")
                return False
        else:
            print(f"❌ Failed to get versions for rollback: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error in rollback test: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing new version management system...")
    print("=" * 60)
    
    # Test 1: Automatische versieverhoging
    versioning_works, prompt_name = test_automatic_versioning()
    
    if versioning_works and prompt_name:
        # Test 2: Versiegeschiedenis API
        history_works = test_version_history_api(prompt_name)
        
        # Test 3: Rollback functionaliteit
        rollback_works = test_rollback_functionality(prompt_name)
        
        print("\n" + "=" * 60)
        print("📊 VERSION MANAGEMENT SYSTEM RESULTS:")
        print(f"  Automatic versioning: {'✅' if versioning_works else '❌'}")
        print(f"  Version history API: {'✅' if history_works else '❌'}")
        print(f"  Rollback functionality: {'✅' if rollback_works else '❌'}")
        
        if versioning_works and history_works and rollback_works:
            print("\n🎉 Version management system is working perfectly!")
            print("   - Automatic versioning ✅")
            print("   - Version history API ✅")
            print("   - Rollback functionality ✅")
        else:
            print("\n⚠️  Some features may not be working correctly")
    else:
        print("\n❌ Basic versioning failed - cannot test other features")
