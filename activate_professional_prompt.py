#!/usr/bin/env python3
"""
Script om de professionele prompt te activeren.
"""

import asyncio
import httpx
import json

# Configuration
API_BASE_URL = "https://v2asbest-tool-production.up.railway.app"
PROMPT_NAME = "analysis_v2_professional"

async def activate_professional_prompt():
    """Activeer de professionele prompt."""
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # First, get the prompt ID
            print(f"🔍 Looking for prompt: {PROMPT_NAME}")
            
            response = await client.get(f"{API_BASE_URL}/admin/prompts/")
            
            if response.status_code == 200:
                prompts = response.json()
                target_prompt = None
                
                for prompt in prompts:
                    if prompt.get('name') == PROMPT_NAME:
                        target_prompt = prompt
                        break
                
                if not target_prompt:
                    print(f"❌ Prompt '{PROMPT_NAME}' not found")
                    return False
                
                prompt_id = target_prompt['id']
                print(f"✅ Found prompt: {PROMPT_NAME} (ID: {prompt_id})")
                
                # Update prompt to active status
                update_data = {
                    "name": target_prompt['name'],
                    "description": target_prompt['description'],
                    "content": target_prompt['content'],
                    "status": "active"
                }
                
                print(f"🚀 Activating prompt...")
                
                response = await client.put(
                    f"{API_BASE_URL}/admin/prompts/{prompt_id}",
                    json=update_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Prompt activated successfully!")
                    print(f"   - ID: {result.get('id')}")
                    print(f"   - Name: {result.get('name')}")
                    print(f"   - Version: {result.get('version')}")
                    print(f"   - Status: {result.get('status')}")
                    
                    return True
                else:
                    print(f"❌ Activation failed: {response.status_code}")
                    print(f"   Response: {response.text}")
                    return False
                    
            else:
                print(f"❌ Failed to get prompts: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error activating prompt: {e}")
            return False

async def main():
    """Main function."""
    print("🔧 Professional Asbest Audit Prompt Activator")
    print("=" * 50)
    
    success = await activate_professional_prompt()
    
    if success:
        print(f"\n🎉 Professional prompt activated successfully!")
        print(f"   The prompt is now ready for use in AI analysis.")
    else:
        print(f"\n❌ Failed to activate professional prompt.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
