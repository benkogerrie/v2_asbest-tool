#!/usr/bin/env python3
"""
Test script om te controleren of database tabellen bestaan
"""

import requests
import json

def test_database_tables():
    """Test of database tabellen bestaan door API calls"""
    base_url = "https://v2asbest-tool-production.up.railway.app"
    
    print("🔍 Testing database tables...")
    
    # Test 1: Try to create a prompt (this will fail if tables don't exist)
    print("\n1. Testing prompt creation (will show error if tables missing)...")
    try:
        test_prompt = {
            "name": "test_prompt_db",
            "description": "Test prompt for database check",
            "content": "This is a test prompt content for database verification.",
            "status": "draft"
        }
        
        response = requests.post(
            f"{base_url}/admin/prompts",
            json=test_prompt,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200 or response.status_code == 201:
            print("   ✅ Database tables exist and prompt creation works")
        elif "relation" in response.text.lower() and "does not exist" in response.text.lower():
            print("   ❌ Database tables don't exist - migration needed")
        elif "table" in response.text.lower() and "doesn't exist" in response.text.lower():
            print("   ❌ Database tables don't exist - migration needed")
        else:
            print(f"   ⚠️  Unexpected response: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Try to list prompts
    print("\n2. Testing prompt listing...")
    try:
        response = requests.get(f"{base_url}/admin/prompts", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            print("   ✅ Prompt listing works")
        else:
            print(f"   ❌ Prompt listing failed: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_database_tables()
