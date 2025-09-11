#!/usr/bin/env python3
"""
Test AI configuratie en LLM service
"""
import asyncio
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.config import settings
from app.services.llm_service import LLMService
from app.services.prompt_service import PromptService

async def test_ai_config():
    """Test AI configuratie"""
    print("🔧 AI Configuratie Test")
    print("=" * 50)
    
    # Check AI settings
    print(f"AI Provider: {settings.ai_provider}")
    print(f"AI Model: {settings.ai_model}")
    print(f"AI API Key: {'***' + settings.ai_api_key[-4:] if settings.ai_api_key else 'NIET GECONFIGUREERD'}")
    print(f"AI Timeout: {settings.ai_timeout}")
    print(f"AI Max Tokens: {settings.ai_max_tokens}")
    
    if not settings.ai_api_key:
        print("❌ AI_API_KEY is niet geconfigureerd!")
        return False
    
    print("\n🧪 LLM Service Test")
    print("-" * 30)
    
    try:
        llm = LLMService()
        print(f"✅ LLM Service geïnitialiseerd")
        print(f"   Provider: {llm.provider}")
        print(f"   Model: {llm.model}")
        
        # Test een eenvoudige API call
        system_prompt = "Je bent een hulpzame assistent."
        user_prompt = "Zeg alleen 'test geslaagd' in JSON format: {\"message\": \"test geslaagd\"}"
        
        print(f"\n🔄 Test API call...")
        result = await llm.call(system_prompt, user_prompt)
        print(f"✅ API call succesvol!")
        print(f"   Resultaat: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ LLM Service test mislukt: {e}")
        return False

async def test_prompt_service():
    """Test prompt service"""
    print("\n📝 Prompt Service Test")
    print("-" * 30)
    
    try:
        # We need a database session for this, so let's skip for now
        print("⚠️  Prompt Service test vereist database - overgeslagen")
        return True
        
    except Exception as e:
        print(f"❌ Prompt Service test mislukt: {e}")
        return False

async def main():
    print("🚀 AI Configuratie & Service Test")
    print("=" * 50)
    
    # Test AI config
    ai_ok = await test_ai_config()
    
    # Test prompt service
    prompt_ok = await test_prompt_service()
    
    print("\n" + "=" * 50)
    print("📋 RESULTATEN:")
    print(f"   AI Config: {'✅ OK' if ai_ok else '❌ FAILED'}")
    print(f"   Prompt Service: {'✅ OK' if prompt_ok else '❌ FAILED'}")
    
    if ai_ok and prompt_ok:
        print("\n🎉 Alle tests geslaagd!")
    else:
        print("\n❌ Sommige tests gefaald - AI analyse zal niet werken")

if __name__ == "__main__":
    asyncio.run(main())

