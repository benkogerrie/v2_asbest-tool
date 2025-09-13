#!/usr/bin/env python3
"""
Test AI configuratie op Railway
"""
import requests
import json

# API Configuration
API_BASE_URL = "https://v2asbest-tool-production.up.railway.app"

def test_ai_config_endpoint():
    """Test of er een AI config endpoint is"""
    print("🔧 Railway AI Config Test")
    print("=" * 50)
    
    try:
        # Test health endpoint first
        response = requests.get(f"{API_BASE_URL}/healthz", timeout=10)
        if response.status_code == 200:
            print("✅ API is bereikbaar")
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
        
        # Try to find AI config endpoint
        endpoints_to_try = [
            "/admin/ai-config",
            "/config/ai",
            "/debug/ai-config",
            "/admin/prompts/test-run"
        ]
        
        for endpoint in endpoints_to_try:
            try:
                response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=10)
                print(f"   {endpoint}: {response.status_code}")
            except:
                print(f"   {endpoint}: Error")
        
        return True
        
    except Exception as e:
        print(f"❌ Railway test failed: {e}")
        return False

def test_prompt_endpoint():
    """Test prompt endpoint"""
    print("\n📝 Prompt Endpoint Test")
    print("-" * 30)
    
    try:
        # Test prompts endpoint
        response = requests.get(f"{API_BASE_URL}/admin/prompts/", timeout=10)
        print(f"Prompts endpoint: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Prompts endpoint werkt")
            print(f"   Aantal prompts: {len(data) if isinstance(data, list) else 'Unknown'}")
            return True
        else:
            print(f"❌ Prompts endpoint failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Prompt test failed: {e}")
        return False

def main():
    print("🚀 Railway AI Configuratie Test")
    print("=" * 50)
    
    # Test AI config
    ai_ok = test_ai_config_endpoint()
    
    # Test prompt endpoint
    prompt_ok = test_prompt_endpoint()
    
    print("\n" + "=" * 50)
    print("📋 RESULTATEN:")
    print(f"   Railway AI Config: {'✅ OK' if ai_ok else '❌ FAILED'}")
    print(f"   Prompt Endpoint: {'✅ OK' if prompt_ok else '❌ FAILED'}")
    
    if not ai_ok or not prompt_ok:
        print("\n❌ AI analyse zal niet werken op Railway!")
        print("💡 Mogelijke oplossingen:")
        print("   1. AI_API_KEY environment variable toevoegen aan Railway")
        print("   2. AI configuratie controleren in Railway dashboard")
        print("   3. Prompts seeden in de database")

if __name__ == "__main__":
    main()


