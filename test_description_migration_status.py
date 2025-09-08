#!/usr/bin/env python3
"""
Test script om te controleren of de description migratie is uitgevoerd
"""
import requests
import json

# Railway production URL
API_BASE_URL = "https://v2asbest-tool-production.up.railway.app"

def test_description_field():
    """Test of de description field nu werkt in de API"""
    print("🔍 Testing description field in API...")
    
    try:
        # Test GET /admin/prompts/ endpoint
        response = requests.get(f"{API_BASE_URL}/admin/prompts/")
        
        if response.status_code == 200:
            prompts = response.json()
            print(f"✅ GET /admin/prompts/ successful - {len(prompts)} prompts found")
            
            # Check if any prompt has a non-null description
            for prompt in prompts:
                print(f"  Prompt '{prompt.get('name')}': description = {prompt.get('description')}")
                if prompt.get('description') is not None:
                    print(f"  🎉 Found non-null description: '{prompt.get('description')}'")
                    return True
            
            print("  ⚠️  All descriptions are still null")
            return False
        else:
            print(f"❌ GET /admin/prompts/ failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing description field: {e}")
        return False

def test_create_prompt_with_description():
    """Test creating a new prompt with description"""
    print("\n🔍 Testing prompt creation with description...")
    
    try:
        # Test data
        prompt_data = {
            "name": "Test Description Field",
            "description": "This is a test description to verify the field works",
            "content": "Test content for description field verification",
            "status": "draft",
            "version": 1
        }
        
        response = requests.post(
            f"{API_BASE_URL}/admin/prompts",
            json=prompt_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            created_prompt = response.json()
            print(f"✅ POST /admin/prompts successful")
            print(f"   Created prompt: {created_prompt.get('name')}")
            print(f"   Description: {created_prompt.get('description')}")
            
            if created_prompt.get('description') == prompt_data['description']:
                print("  🎉 Description field is working correctly!")
                return True
            else:
                print("  ⚠️  Description was not saved correctly")
                return False
        else:
            print(f"❌ POST /admin/prompts failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating prompt with description: {e}")
        return False

def test_health_endpoint():
    """Test de health endpoint voor Mixed Content issues"""
    print("\n🔍 Testing health endpoint...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/healthz")
        
        if response.status_code == 200:
            print("✅ /healthz endpoint accessible")
            return True
        else:
            print(f"❌ /healthz failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing health endpoint: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing description migration status...")
    print("=" * 50)
    
    # Test 1: Check existing prompts
    description_works = test_description_field()
    
    # Test 2: Try creating a new prompt with description
    creation_works = test_create_prompt_with_description()
    
    # Test 3: Check health endpoint
    health_works = test_health_endpoint()
    
    print("\n" + "=" * 50)
    print("📊 SUMMARY:")
    print(f"  Description field working: {'✅' if description_works else '❌'}")
    print(f"  Prompt creation with description: {'✅' if creation_works else '❌'}")
    print(f"  Health endpoint accessible: {'✅' if health_works else '❌'}")
    
    if description_works and creation_works:
        print("\n🎉 Description migration appears to be working!")
    else:
        print("\n⚠️  Description migration may not be complete yet")
