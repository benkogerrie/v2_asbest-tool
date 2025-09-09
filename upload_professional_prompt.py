#!/usr/bin/env python3
"""
Script om de professionele asbest audit prompt te uploaden naar het systeem.
"""

import asyncio
import httpx
import json
import os
from pathlib import Path

# Configuration
API_BASE_URL = "https://v2asbest-tool-production.up.railway.app"
PROMPT_FILE = "seeds/analysis_v2_professional.md"

async def upload_professional_prompt():
    """Upload de professionele prompt naar het systeem."""
    
    # Read the prompt content
    if not Path(PROMPT_FILE).exists():
        print(f"❌ Prompt file not found: {PROMPT_FILE}")
        return False
    
    with open(PROMPT_FILE, 'r', encoding='utf-8') as f:
        prompt_content = f.read()
    
    print(f"📖 Read prompt content: {len(prompt_content)} characters")
    
    # Create prompt data
    prompt_data = {
        "name": "analysis_v2_professional",
        "description": "Professionele asbest audit prompt met 275-punten checklist volgens NEN standaarden",
        "content": prompt_content,
        "status": "draft"  # Start as draft, can be activated later
    }
    
    print(f"📝 Prompt data prepared:")
    print(f"   - Name: {prompt_data['name']}")
    print(f"   - Description: {prompt_data['description']}")
    print(f"   - Content length: {len(prompt_data['content'])} chars")
    print(f"   - Status: {prompt_data['status']}")
    
    # Upload prompt
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            print(f"\n🚀 Uploading prompt to {API_BASE_URL}/admin/prompts/")
            
            response = await client.post(
                f"{API_BASE_URL}/admin/prompts/",
                json=prompt_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Prompt uploaded successfully!")
                print(f"   - ID: {result.get('id')}")
                print(f"   - Name: {result.get('name')}")
                print(f"   - Version: {result.get('version')}")
                print(f"   - Status: {result.get('status')}")
                
                # Test the prompt
                print(f"\n🧪 Testing the uploaded prompt...")
                await test_prompt(result.get('id'))
                
                return True
            else:
                print(f"❌ Upload failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error uploading prompt: {e}")
            return False

async def test_prompt(prompt_id):
    """Test the uploaded prompt with sample text."""
    
    test_text = """
    ASBESTINVENTARISATIE RAPPORT
    
    Project: Test Project 2024
    Opdrachtgever: Test BV
    Adres: Teststraat 123, 1234 AB Teststad
    
    Autorisatiedatum: 15-03-2024
    Geldigheidsdatum: 15-03-2026
    
    SAMENVATTING:
    Bron A001: Asbesthoudende plaat in keuken
    Bron A002: Asbesthoudende buis in kelder
    
    CONCLUSIE:
    Rapport is geschikt voor het beoogde doel.
    """
    
    test_data = {
        "test_text": test_text
    }
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            print(f"   Testing prompt {prompt_id} with sample text...")
            
            response = await client.post(
                f"{API_BASE_URL}/admin/prompts/{prompt_id}/test",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Prompt test successful!")
                print(f"   - Score: {result.get('score', 'N/A')}")
                print(f"   - Findings count: {len(result.get('findings', []))}")
                
                # Show first few findings
                findings = result.get('findings', [])
                if findings:
                    print(f"   - First finding: {findings[0].get('title', 'N/A')}")
                
                return True
            else:
                print(f"   ❌ Prompt test failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error testing prompt: {e}")
            return False

async def main():
    """Main function."""
    print("🔧 Professional Asbest Audit Prompt Uploader")
    print("=" * 50)
    
    success = await upload_professional_prompt()
    
    if success:
        print(f"\n🎉 Professional prompt uploaded and tested successfully!")
        print(f"   You can now activate it in the System Owner interface.")
    else:
        print(f"\n❌ Failed to upload professional prompt.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
