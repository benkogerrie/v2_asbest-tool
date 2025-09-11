#!/usr/bin/env python3
"""
Test AI configuratie in Railway cloud via API endpoints
"""
import requests
import json
import time
from typing import Dict, Any

# Vervang dit met je echte Railway API URL
RAILWAY_API_URL = "https://v2asbest-tool-production.up.railway.app"

def test_railway_health():
    """Test Railway health endpoint"""
    print("🏥 Railway Health Check")
    print("=" * 50)
    
    try:
        response = requests.get(f"{RAILWAY_API_URL}/healthz", timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Health Check OK")
            print(f"   Status: {health_data.get('status', 'unknown')}")
            print(f"   Database: {health_data.get('checks', {}).get('database', 'unknown')}")
            print(f"   Redis: {health_data.get('checks', {}).get('redis', 'unknown')}")
            return True
        else:
            print(f"❌ Health Check Failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Health Check Error: {e}")
        return False

def test_ai_config_endpoint():
    """Test AI configuratie via API endpoint"""
    print("\n🤖 AI Configuratie Test")
    print("=" * 50)
    
    try:
        # Test AI config endpoint
        response = requests.get(f"{RAILWAY_API_URL}/admin/ai-configurations", timeout=10)
        print(f"AI Config Status: {response.status_code}")
        
        if response.status_code == 200:
            config_data = response.json()
            print(f"✅ AI Config Endpoint OK")
            if isinstance(config_data, list) and len(config_data) > 0:
                config = config_data[0]  # Take first config
                print(f"   Provider: {config.get('provider', 'unknown')}")
                print(f"   Model: {config.get('model', 'unknown')}")
                print(f"   API Key: {'***' + config.get('api_key', '')[-4:] if config.get('api_key') else 'NOT SET'}")
            else:
                print(f"   Config data: {config_data}")
            return True
        else:
            print(f"⚠️  AI Config Endpoint: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ AI Config Error: {e}")
        return False

def test_ai_analysis_endpoint():
    """Test AI analysis endpoint met een test prompt"""
    print("\n🧪 AI Analysis Test")
    print("=" * 50)
    
    try:
        # Test data voor AI analysis
        test_data = {
            "text": "Dit is een test tekst voor AI analyse.",
            "prompt_type": "analysis"
        }
        
        response = requests.post(
            f"{RAILWAY_API_URL}/api/ai/analyze", 
            json=test_data,
            timeout=30
        )
        
        print(f"AI Analysis Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ AI Analysis OK")
            print(f"   Result: {result}")
            return True
        else:
            print(f"❌ AI Analysis Failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ AI Analysis Error: {e}")
        return False

def test_prompts_endpoint():
    """Test prompts endpoint"""
    print("\n📝 Prompts Test")
    print("=" * 50)
    
    try:
        response = requests.get(f"{RAILWAY_API_URL}/admin/prompts", timeout=10)
        print(f"Prompts Status: {response.status_code}")
        
        if response.status_code == 200:
            prompts = response.json()
            print(f"✅ Prompts Endpoint OK")
            print(f"   Aantal prompts: {len(prompts) if isinstance(prompts, list) else 'unknown'}")
            return True
        else:
            print(f"⚠️  Prompts Endpoint: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Prompts Error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Railway Cloud AI Test")
    print("=" * 50)
    print(f"Testing: {RAILWAY_API_URL}")
    print()
    
    # Check if URL is configured
    if "your-railway-app" in RAILWAY_API_URL:
        print("❌ Please update RAILWAY_API_URL with your actual Railway URL")
        print("   Edit this file and replace 'your-railway-app' with your real URL")
        return
    
    results = []
    
    # Run tests
    results.append(("Health Check", test_railway_health()))
    results.append(("AI Config", test_ai_config_endpoint()))
    results.append(("Prompts", test_prompts_endpoint()))
    results.append(("AI Analysis", test_ai_analysis_endpoint()))
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 RESULTATEN:")
    for test_name, success in results:
        status = "✅ OK" if success else "❌ FAILED"
        print(f"   {test_name}: {status}")
    
    all_passed = all(success for _, success in results)
    if all_passed:
        print("\n🎉 Alle tests geslaagd! Railway AI configuratie werkt correct.")
    else:
        print("\n⚠️  Sommige tests gefaald. Controleer Railway logs voor details.")

if __name__ == "__main__":
    main()
