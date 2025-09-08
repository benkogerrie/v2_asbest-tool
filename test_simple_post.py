#!/usr/bin/env python3
"""
Eenvoudige test voor POST endpoint
"""
import requests
import json

# Railway production URL
API_BASE_URL = "https://v2asbest-tool-production.up.railway.app"

def test_simple_post():
    """Test eenvoudige POST request"""
    print("🔍 Testing simple POST request...")
    
    try:
        prompt_data = {
            "name": "Simple Test",
            "description": "Simple test prompt",
            "content": "This is a simple test",
            "status": "draft"
        }
        
        print(f"📝 Sending POST request...")
        print(f"   Data: {prompt_data}")
        
        response = requests.post(
            f"{API_BASE_URL}/admin/prompts",
            json=prompt_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📝 Response received:")
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"   Response type: {type(response_data)}")
            print(f"   Response content: {response_data}")
            
            if isinstance(response_data, list):
                print(f"   ⚠️  Response is a list with {len(response_data)} items")
                if len(response_data) > 0:
                    print(f"   First item: {response_data[0]}")
            else:
                print(f"   ✅ Response is a single object")
                
        else:
            print(f"   ❌ Request failed")
            print(f"   Response text: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_simple_post()
