#!/usr/bin/env python3
"""
Debug script voor Anthropic API call
"""
import asyncio
import httpx
import json

async def debug_anthropic_api():
    print("🔍 Debugging Anthropic API Call...")
    
    # Test data
    api_key = "YOUR_API_KEY_HERE"  # Replace with actual API key for testing
    model = "claude-3-5-haiku-20241022"
    
    system_prompt = "Je bent een QA-assistent. Geef alleen JSON terug."
    user_prompt = "Test content"
    
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": api_key,
        "content-type": "application/json",
        "anthropic-version": "2023-06-01"
    }
    body = {
        "model": model,
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_prompt}],
        "max_tokens": 1000,
    }
    
    print(f"URL: {url}")
    print(f"Headers: {headers}")
    print(f"Body: {json.dumps(body, indent=2)}")
    
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(url, headers=headers, json=body)
            print(f"\nStatus: {resp.status_code}")
            print(f"Response: {resp.text}")
            
            if resp.status_code == 200:
                data = resp.json()
                print(f"Success! Content: {data}")
            else:
                print(f"Error: {resp.status_code} - {resp.text}")
                
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    asyncio.run(debug_anthropic_api())
