#!/usr/bin/env python3
"""
Test script om de migratie chain te controleren
"""
import requests
import json

# Railway production URL
API_BASE_URL = "https://v2asbest-tool-production.up.railway.app"

def test_migration_status():
    """Test de migratie status via de API"""
    print("🔍 Testing migration status...")
    
    try:
        # Test of de prompts tabel bestaat door een GET request
        response = requests.get(f"{API_BASE_URL}/admin/prompts/")
        
        if response.status_code == 200:
            prompts = response.json()
            print(f"✅ Prompts table exists - {len(prompts)} prompts found")
            
            # Check if any prompt has a description field
            if len(prompts) > 0:
                sample_prompt = prompts[0]
                print(f"   Sample prompt fields: {list(sample_prompt.keys())}")
                
                if 'description' in sample_prompt:
                    print("   ✅ Description field exists in API response")
                    if sample_prompt.get('description') is not None:
                        print("   🎉 Description field is working!")
                        return True
                    else:
                        print("   ⚠️  Description field exists but is null")
                        return False
                else:
                    print("   ❌ Description field missing from API response")
                    return False
            else:
                print("   ⚠️  No prompts found to test")
                return False
        else:
            print(f"❌ Prompts endpoint failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing migration status: {e}")
        return False

def test_direct_column_check():
    """Test door een prompt te maken met description"""
    print("\n🔍 Testing direct column creation...")
    
    try:
        # Maak een nieuwe prompt aan met description
        prompt_data = {
            "name": "Migration Test",
            "description": "Testing if description column exists",
            "content": "Test content",
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
            
            if created_prompt.get('description') == prompt_data['description']:
                print("   🎉 Description column is working!")
                return True
            else:
                print("   ❌ Description was not saved correctly")
                return False
        else:
            print(f"❌ Prompt creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing direct column: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing migration chain and description field...")
    print("=" * 60)
    
    # Test 1: Check current migration status
    migration_works = test_migration_status()
    
    # Test 2: Try direct column creation
    column_works = test_direct_column_check()
    
    print("\n" + "=" * 60)
    print("📊 MIGRATION STATUS:")
    print(f"  Migration status check: {'✅' if migration_works else '❌'}")
    print(f"  Direct column test: {'✅' if column_works else '❌'}")
    
    if migration_works and column_works:
        print("\n🎉 Description migration is working correctly!")
    elif migration_works and not column_works:
        print("\n⚠️  Description field exists but may not be working properly")
    else:
        print("\n❌ Description migration has not been applied yet")
        print("   The migration may be pending or failed")