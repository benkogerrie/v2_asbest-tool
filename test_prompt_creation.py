#!/usr/bin/env python3
"""
Test script om te controleren of prompt creation nu werkt met de juiste data
"""

import requests
import json

def test_prompt_creation():
    """Test prompt creation met verschillende data scenarios"""
    base_url = "https://v2asbest-tool-production.up.railway.app"
    
    print("Testing prompt creation with different data scenarios...")
    
    # Test 1: Minimale data (zoals "1" in alle velden)
    print("\n=== Test 1: Minimale data ===")
    minimal_data = {
        "name": "1",
        "content": "1", 
        "version": 1,
        "status": "draft"
    }
    
    try:
        response = requests.post(
            f"{base_url}/admin/prompts/",
            json=minimal_data,
            timeout=10
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
        
        if response.status_code == 200:
            print("✅ Minimale data werkt!")
        else:
            print("❌ Minimale data faalt")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Realistische data
    print("\n=== Test 2: Realistische data ===")
    realistic_data = {
        "name": "test_prompt",
        "content": "Dit is een test prompt voor asbest analyse.",
        "version": 1,
        "status": "draft"
    }
    
    try:
        response = requests.post(
            f"{base_url}/admin/prompts/",
            json=realistic_data,
            timeout=10
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
        
        if response.status_code == 200:
            print("✅ Realistische data werkt!")
        else:
            print("❌ Realistische data faalt")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Data zonder version (zoals de oude UI)
    print("\n=== Test 3: Data zonder version ===")
    no_version_data = {
        "name": "test_no_version",
        "content": "Test zonder version veld",
        "status": "draft"
    }
    
    try:
        response = requests.post(
            f"{base_url}/admin/prompts/",
            json=no_version_data,
            timeout=10
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
        
        if response.status_code == 422:
            print("❌ Zoals verwacht: version veld is verplicht")
        else:
            print("✅ Onverwacht: werkt zonder version")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "="*60)
    print("CONCLUSIE:")
    print("Als Test 1 en 2 werken, dan is de UI fix correct.")
    print("Als Test 3 faalt met 422, dan was dat het probleem.")
    print("="*60)

if __name__ == "__main__":
    test_prompt_creation()
