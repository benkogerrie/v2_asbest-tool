#!/usr/bin/env python3
"""
Gedetailleerde test voor versiebeheer van prompts
"""
import requests
import json

# Railway production URL
API_BASE_URL = "https://v2asbest-tool-production.up.railway.app"

def test_version_creation():
    """Test het aanmaken van verschillende versies"""
    print("🔍 Testing version creation in detail...")
    
    try:
        # Test 1: Maak een unieke prompt aan
        print("\n📝 Creating unique prompt with version 1...")
        prompt_v1 = {
            "name": "Version Test Detailed",
            "description": "Testing detailed version management",
            "content": "This is version 1 content",
            "status": "draft",
            "version": 1
        }
        
        response_v1 = requests.post(
            f"{API_BASE_URL}/admin/prompts",
            json=prompt_v1,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Response status: {response_v1.status_code}")
        print(f"Response type: {type(response_v1.json())}")
        print(f"Response content: {response_v1.json()}")
        
        if response_v1.status_code == 200:
            result_v1 = response_v1.json()
            
            # Handle list response
            if isinstance(result_v1, list):
                print(f"⚠️  POST returned a list with {len(result_v1)} items")
                if len(result_v1) > 0:
                    created_v1 = result_v1[0]
                else:
                    print("❌ Empty list returned")
                    return False
            else:
                created_v1 = result_v1
            
            print(f"✅ Version 1 created successfully")
            print(f"   ID: {created_v1.get('id')}")
            print(f"   Name: {created_v1.get('name')}")
            print(f"   Version: {created_v1.get('version')}")
            
            # Test 2: Probeer versie 2 van dezelfde prompt
            print(f"\n📝 Creating version 2 of same prompt...")
            prompt_v2 = {
                "name": "Version Test Detailed",  # Zelfde naam
                "description": "Testing detailed version management",
                "content": "This is version 2 content",
                "status": "draft",
                "version": 2
            }
            
            response_v2 = requests.post(
                f"{API_BASE_URL}/admin/prompts",
                json=prompt_v2,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Response status: {response_v2.status_code}")
            print(f"Response content: {response_v2.json()}")
            
            if response_v2.status_code == 200:
                result_v2 = response_v2.json()
                
                if isinstance(result_v2, list):
                    if len(result_v2) > 0:
                        created_v2 = result_v2[0]
                    else:
                        print("❌ Empty list returned for version 2")
                        return False
                else:
                    created_v2 = result_v2
                
                print(f"✅ Version 2 created successfully")
                print(f"   ID: {created_v2.get('id')}")
                print(f"   Name: {created_v2.get('name')}")
                print(f"   Version: {created_v2.get('version')}")
                
                # Check if IDs are different (should be different records)
                if created_v1.get('id') != created_v2.get('id'):
                    print("   🎉 Different IDs - versions are separate records!")
                    return True
                else:
                    print("   ⚠️  Same ID - versions may be overwriting each other")
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
        print(f"❌ Error in version creation test: {e}")
        return False

def test_database_constraint():
    """Test of de database constraint werkt"""
    print("\n🔍 Testing database constraint...")
    
    try:
        # Probeer exact dezelfde naam en versie aan te maken
        print("📝 Attempting to create duplicate name+version...")
        duplicate_prompt = {
            "name": "Duplicate Test",
            "description": "Testing duplicate constraint",
            "content": "This should fail due to constraint",
            "status": "draft",
            "version": 1
        }
        
        # Eerste keer
        response1 = requests.post(
            f"{API_BASE_URL}/admin/prompts",
            json=duplicate_prompt,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"First creation - Status: {response1.status_code}")
        
        if response1.status_code == 200:
            # Tweede keer - zou moeten falen
            response2 = requests.post(
                f"{API_BASE_URL}/admin/prompts",
                json=duplicate_prompt,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Second creation - Status: {response2.status_code}")
            
            if response2.status_code == 400 or response2.status_code == 409:
                print("   🎉 Constraint working - duplicate rejected!")
                return True
            elif response2.status_code == 200:
                print("   ⚠️  Constraint not working - duplicate allowed")
                return False
            else:
                print(f"   ❌ Unexpected status: {response2.status_code}")
                return False
        else:
            print(f"   ❌ First creation failed: {response1.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing constraint: {e}")
        return False

def check_all_prompts():
    """Check alle prompts in de database"""
    print("\n🔍 Checking all prompts in database...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/admin/prompts/")
        
        if response.status_code == 200:
            prompts = response.json()
            print(f"✅ Found {len(prompts)} total prompts")
            
            # Groepeer per naam
            by_name = {}
            for prompt in prompts:
                name = prompt.get('name')
                if name not in by_name:
                    by_name[name] = []
                by_name[name].append(prompt)
            
            print(f"   Unique prompt names: {len(by_name)}")
            
            # Toon versies per naam
            for name, versions in by_name.items():
                print(f"   '{name}': {len(versions)} version(s)")
                for version in versions:
                    print(f"     - v{version.get('version')}: {version.get('content')[:50]}...")
            
            return True
        else:
            print(f"❌ Failed to get prompts: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking prompts: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Detailed version management testing...")
    print("=" * 60)
    
    # Test 1: Versie aanmaak
    version_creation_works = test_version_creation()
    
    # Test 2: Database constraint
    constraint_works = test_database_constraint()
    
    # Test 3: Check alle prompts
    check_all_prompts()
    
    print("\n" + "=" * 60)
    print("📊 DETAILED RESULTS:")
    print(f"  Version creation: {'✅' if version_creation_works else '❌'}")
    print(f"  Database constraint: {'✅' if constraint_works else '❌'}")
    
    if version_creation_works and constraint_works:
        print("\n🎉 Version management is working correctly!")
    else:
        print("\n⚠️  Version management has issues")
        print("   - Check database schema and constraints")
        print("   - Verify API endpoint behavior")
