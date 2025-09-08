#!/usr/bin/env python3
"""
Test script voor AI setup op Railway - controleer configuratie en seed prompt
"""
import asyncio
import os
import httpx

async def test_railway_ai_setup():
    print("🔍 Testing Railway AI Setup...")
    print("=" * 50)
    
    base_url = "https://v2asbest-tool-production.up.railway.app"
    
    # 1. Test health endpoint
    print("🏥 Health Check:")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/healthz")
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                print("  ✅ API is healthy")
            else:
                print("  ❌ API health check failed")
    except Exception as e:
        print(f"  ❌ Connection failed: {e}")
        return
    
    # 2. Test prompts endpoint
    print("\n📋 Prompts Check:")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/admin/prompts/")
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                prompts = response.json()
                print(f"  Total prompts: {len(prompts)}")
                
                active_prompts = [p for p in prompts if p.get('status') == 'active']
                print(f"  Active prompts: {len(active_prompts)}")
                
                analysis_prompts = [p for p in prompts if p.get('name') == 'analysis_v1']
                print(f"  analysis_v1 prompts: {len(analysis_prompts)}")
                
                for prompt in analysis_prompts:
                    print(f"    - v{prompt.get('version')} ({prompt.get('status')})")
                
                if not active_prompts:
                    print("  ⚠️  No active prompts found - need to seed")
                elif not analysis_prompts:
                    print("  ⚠️  No analysis_v1 prompt found - need to seed")
                else:
                    print("  ✅ Prompts are ready!")
            else:
                print(f"  ❌ Prompts endpoint failed: {response.text}")
    except Exception as e:
        print(f"  ❌ Prompts check failed: {e}")
    
    # 3. Test test-run endpoint (if prompts exist)
    print("\n🧪 Test-run Endpoint Check:")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/admin/prompts/")
            if response.status_code == 200:
                prompts = response.json()
                active_prompts = [p for p in prompts if p.get('status') == 'active']
                
                if active_prompts:
                    prompt_id = active_prompts[0]['id']
                    print(f"  Testing with prompt: {active_prompts[0]['name']} (v{active_prompts[0]['version']})")
                    
                    # Test test-run endpoint
                    test_payload = {
                        "sample_text": "Dit is een test PDF content voor AI analyse."
                    }
                    
                    response = await client.post(
                        f"{base_url}/admin/prompts/{prompt_id}/test-run",
                        json=test_payload
                    )
                    print(f"  Test-run status: {response.status_code}")
                    
                    if response.status_code == 200:
                        result = response.json()
                        print("  ✅ Test-run endpoint works!")
                        print(f"  Success: {result.get('success', 'unknown')}")
                    else:
                        print(f"  ❌ Test-run failed: {response.text}")
                else:
                    print("  ⚠️  No active prompts to test with")
            else:
                print("  ❌ Cannot get prompts for test-run")
    except Exception as e:
        print(f"  ❌ Test-run check failed: {e}")
    
    print("\n🎯 Next Steps:")
    print("  1. Check if AI_API_KEY is set in Railway environment")
    print("  2. If no prompts: run seed script on Railway")
    print("  3. Test LLM service with real API calls")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(test_railway_ai_setup())
