#!/usr/bin/env python3
"""
Seed de analysis_v1 prompt op Railway via API
"""
import asyncio
import httpx
from pathlib import Path

async def seed_analysis_v1():
    print("🌱 Seeding analysis_v1 prompt op Railway...")
    
    base_url = "https://v2asbest-tool-production.up.railway.app"
    
    # Lees de prompt content
    prompt_file = Path(__file__).parent / "seeds" / "analysis_v1.md"
    if not prompt_file.exists():
        print("❌ analysis_v1.md not found!")
        return
    
    content = prompt_file.read_text(encoding="utf-8")
    
    # Maak de prompt via API
    prompt_data = {
        "name": "analysis_v1",
        "description": "AI analyse prompt voor asbest rapporten - controleert checklist items en genereert JSON output",
        "role": "system",
        "content": content,
        "status": "active"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            print("📤 Creating analysis_v1 prompt...")
            response = await client.post(
                f"{base_url}/admin/prompts/",
                json=prompt_data
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ analysis_v1 prompt created successfully!")
                print(f"  ID: {result['id']}")
                print(f"  Version: {result['version']}")
                print(f"  Status: {result['status']}")
            else:
                print(f"❌ Failed to create prompt: {response.text}")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(seed_analysis_v1())
