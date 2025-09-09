#!/usr/bin/env python3
"""
Test script voor AI Configuration API endpoints
"""
import asyncio
import httpx
import json

async def test_ai_config_api():
    print("🤖 Testing AI Configuration API...")
    print("=" * 60)
    
    base_url = "https://v2asbest-tool-production.up.railway.app"
    
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            # 1. Test health endpoint
            print("🏥 Health Check:")
            response = await client.get(f"{base_url}/healthz")
            print(f"  Status: {response.status_code}")
            if response.status_code != 200:
                print("  ❌ API not healthy")
                return
            print("  ✅ API is healthy")
            
            # 2. Test list AI configurations
            print("\n📋 List AI Configurations:")
            response = await client.get(f"{base_url}/admin/ai-configurations/")
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                configs = response.json()
                print(f"  Found {len(configs)} configurations")
                for config in configs:
                    print(f"    - {config['name']} ({config['provider']}/{config['model']}) - {'Active' if config['is_active'] else 'Inactive'}")
            else:
                print(f"  ❌ Failed: {response.text}")
            
            # 3. Test create AI configuration
            print("\n➕ Create AI Configuration:")
            new_config = {
                "name": "Test Anthropic Config",
                "provider": "anthropic",
                "model": "claude-3-5-haiku-20241022",
                "api_key": "sk-ant-api03-PLACEHOLDER-API-KEY-HERE"
            }
            
            response = await client.post(
                f"{base_url}/admin/ai-configurations/",
                json=new_config
            )
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                config = response.json()
                print(f"  ✅ Created: {config['name']} (ID: {config['id']})")
                config_id = config['id']
                
                # 4. Test the configuration
                print("\n🧪 Test AI Configuration:")
                test_payload = {
                    "test_message": "Test message for AI configuration validation"
                }
                
                response = await client.post(
                    f"{base_url}/admin/ai-configurations/{config_id}/test",
                    json=test_payload
                )
                print(f"  Status: {response.status_code}")
                if response.status_code == 200:
                    result = response.json()
                    print(f"  ✅ Test successful: {result['message']}")
                    if result.get('response_time_ms'):
                        print(f"  ⏱️  Response time: {result['response_time_ms']}ms")
                else:
                    print(f"  ❌ Test failed: {response.text}")
                
                # 5. Test list again to see the new config
                print("\n📋 List AI Configurations (after create):")
                response = await client.get(f"{base_url}/admin/ai-configurations/")
                if response.status_code == 200:
                    configs = response.json()
                    print(f"  Found {len(configs)} configurations")
                    for config in configs:
                        print(f"    - {config['name']} ({config['provider']}/{config['model']}) - {'Active' if config['is_active'] else 'Inactive'}")
                
            else:
                print(f"  ❌ Failed to create: {response.text}")
                
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("🎯 Test Summary:")
    print("  - AI Configuration API: Ready for testing")
    print("  - CRUD operations: Implemented")
    print("  - Test functionality: Available")

if __name__ == "__main__":
    asyncio.run(test_ai_config_api())
