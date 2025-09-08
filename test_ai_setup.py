#!/usr/bin/env python3
"""
Test script voor AI setup - controleer configuratie en seed prompt
"""
import asyncio
import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.prompt import Prompt
from app.config import settings

async def test_ai_setup():
    print("🔍 Testing AI Setup...")
    print("=" * 50)
    
    # 1. Test configuratie
    print("📋 AI Configuration:")
    print(f"  Provider: {settings.ai_provider}")
    print(f"  Model: {settings.ai_model}")
    print(f"  API Key: {'✅ Set' if settings.ai_api_key else '❌ Missing'}")
    print(f"  Timeout: {settings.ai_timeout}s")
    print(f"  Max Tokens: {settings.ai_max_tokens}")
    print()
    
    # 2. Test database connection en prompts
    print("🗄️ Database & Prompts:")
    async for session in get_db():
        # Check voor actieve prompts
        result = await session.execute(
            select(Prompt).where(Prompt.status == "active")
        )
        active_prompts = result.scalars().all()
        
        print(f"  Active prompts: {len(active_prompts)}")
        for prompt in active_prompts:
            print(f"    - {prompt.name} (v{prompt.version})")
        
        # Check voor analysis_v1 specifiek
        result = await session.execute(
            select(Prompt).where(Prompt.name == "analysis_v1")
        )
        analysis_prompts = result.scalars().all()
        
        print(f"  analysis_v1 prompts: {len(analysis_prompts)}")
        for prompt in analysis_prompts:
            print(f"    - v{prompt.version} ({prompt.status})")
        
        break
    
    print()
    print("🎯 Next Steps:")
    if not settings.ai_api_key:
        print("  1. Set AI_API_KEY environment variable")
    if not active_prompts:
        print("  2. Run: python seeds/seed_prompts.py")
    if settings.ai_api_key and active_prompts:
        print("  3. Ready to test LLM service!")
    
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(test_ai_setup())
