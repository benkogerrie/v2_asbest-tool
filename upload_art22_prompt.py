#!/usr/bin/env python3
"""
Upload Art.22 prompt naar het systeem
"""

import asyncio
import httpx
import json
from pathlib import Path

async def upload_art22_prompt():
    print("🔧 Art.22 Prompt Uploader")
    print("=" * 50)
    
    # Load the Art.22 prompt
    prompt_path = Path("seeds/analysis_art22_v1.md")
    if not prompt_path.exists():
        print("❌ Art.22 prompt not found!")
        return
    
    with open(prompt_path, 'r', encoding='utf-8') as f:
        prompt_content = f.read()
    
    print(f"📖 Loaded Art.22 prompt: {len(prompt_content)} characters")
    
    # API configuration
    base_url = "https://v2asbest-tool-production.up.railway.app"
    token = "your-system-owner-token-here"  # Replace with actual token
    
    # Prompt data
    prompt_data = {
        "name": "analysis_art22_v1",
        "description": "AI Prompt voor Asbestinventarisatierapport Audit - Artikel 22. Wettelijke compliance checklist met 14 specifieke items voor asbestinventarisatierapporten.",
        "content": prompt_content,
        "status": "draft"
    }
    
    print(f"📤 Uploading prompt: {prompt_data['name']}")
    print(f"   Description: {prompt_data['description']}")
    print(f"   Status: {prompt_data['status']}")
    
    try:
        async with httpx.AsyncClient() as client:
            # Create the prompt
            response = await client.post(
                f"{base_url}/admin/prompts/",
                json=prompt_data,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Prompt uploaded successfully!")
                print(f"   ID: {result['id']}")
                print(f"   Name: {result['name']}")
                print(f"   Version: {result['version']}")
                print(f"   Status: {result['status']}")
                
                # Activate the prompt
                print(f"\n🔄 Activating prompt...")
                activate_response = await client.post(
                    f"{base_url}/admin/prompts/{result['id']}/activate",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json"
                    }
                )
                
                if activate_response.status_code == 200:
                    activate_result = activate_response.json()
                    print(f"✅ Prompt activated successfully!")
                    print(f"   Status: {activate_result['status']}")
                else:
                    print(f"❌ Failed to activate prompt: {activate_response.status_code}")
                    print(f"   Response: {activate_response.text}")
                
            else:
                print(f"❌ Failed to upload prompt: {response.status_code}")
                print(f"   Response: {response.text}")
                
    except Exception as e:
        print(f"❌ Error during upload: {e}")

if __name__ == "__main__":
    print("⚠️  Note: This script requires a valid system owner token.")
    print("   Please update the 'token' variable with your actual token.")
    print("   You can get this from the browser's localStorage after logging in.")
    print()
    
    # For now, just show what would be uploaded
    print("📋 Prompt data that would be uploaded:")
    prompt_path = Path("seeds/analysis_art22_v1.md")
    if prompt_path.exists():
        with open(prompt_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"   Name: analysis_art22_v1")
        print(f"   Description: AI Prompt voor Asbestinventarisatierapport Audit - Artikel 22")
        print(f"   Content length: {len(content)} characters")
        print(f"   Status: draft")
        print()
        print("   Content preview:")
        print(f"   {content[:200]}...")
    else:
        print("   ❌ Art.22 prompt file not found!")
