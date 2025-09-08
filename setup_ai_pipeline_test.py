#!/usr/bin/env python3
"""
Setup script voor AI pipeline testing
Maakt een actieve AI configuratie en prompt aan voor testing
"""

import requests
import json
import time
from datetime import datetime

# Configuration
API_BASE_URL = "https://v2asbest-tool-production.up.railway.app"

def setup_ai_pipeline():
    """Setup AI configuration and prompt for pipeline testing"""
    print("🔧 Setting up AI Pipeline for Testing...")
    print("=" * 60)
    
    # Step 1: Create AI Configuration
    print("🤖 Creating AI Configuration:")
    try:
        ai_config = {
            "name": f"Pipeline Test Config {int(time.time())}",
            "provider": "anthropic",
            "model": "claude-3-5-haiku-20241022",
            "api_key": "sk-ant-test-key-for-pipeline-testing",
            "is_active": True
        }
        
        response = requests.post(
            f"{API_BASE_URL}/admin/ai-configurations/",
            json=ai_config,
            timeout=10
        )
        
        if response.status_code == 200:
            created_config = response.json()
            config_id = created_config['id']
            print(f"  ✅ Created: {created_config['name']} (ID: {config_id})")
        else:
            print(f"  ❌ Failed to create AI config: {response.text}")
            return False
    except Exception as e:
        print(f"  ❌ AI config creation error: {e}")
        return False
    
    # Step 2: Check if active prompt exists
    print("\n📝 Checking Active Prompt:")
    try:
        response = requests.get(f"{API_BASE_URL}/admin/prompts/", timeout=10)
        if response.status_code == 200:
            prompts = response.json()
            active_prompts = [p for p in prompts if p.get('status') == 'active']
            if active_prompts:
                print(f"  ✅ Found {len(active_prompts)} active prompt(s)")
                for prompt in active_prompts:
                    print(f"    - {prompt['name']} (v{prompt['version']})")
            else:
                print("  ⚠️  No active prompts found, creating one...")
                
                # Create a test prompt
                test_prompt = {
                    "name": "analysis_v1",
                    "description": "Test prompt for AI pipeline testing",
                    "content": """Je bent een expert in asbest inventarisatie rapporten. Analyseer het volgende rapport en geef een beoordeling.

CHECKLIST:
- Scope van onderzoek
- Risicobeoordeling  
- Handtekening inspecteur
- Wettelijk kader
- Methode van onderzoek
- Locatiegegevens
- Monstergegevens
- Foto's en bewijs
- Aanbevelingen

SEVERITY_WEIGHTS: {"CRITICAL":30,"HIGH":15,"MEDIUM":7,"LOW":3}

Geef je analyse terug in het volgende JSON formaat:
{
  "report_summary": "Korte samenvatting van het rapport",
  "score": 85,
  "findings": [
    {
      "code": "SCOPE_001",
      "title": "Scope van onderzoek ontbreekt",
      "category": "FORMAL",
      "severity": "HIGH",
      "status": "FAIL",
      "page": 1,
      "evidence_snippet": "Geen duidelijke scope beschrijving gevonden",
      "suggested_fix": "Voeg een duidelijke scope sectie toe"
    }
  ]
}

OUTPUT_SCHEMA:
{
  "report_summary": "string",
  "score": "number (0-100)",
  "findings": [
    {
      "code": "string",
      "title": "string", 
      "category": "FORMAL|CONTENT|RISK|CONSISTENCY|ADMIN",
      "severity": "LOW|MEDIUM|HIGH|CRITICAL",
      "status": "PASS|FAIL|UNKNOWN",
      "page": "number (optional)",
      "evidence_snippet": "string (max 300 chars)",
      "suggested_fix": "string (optional)"
    }
  ]
}""",
                    "status": "active"
                }
                
                response = requests.post(
                    f"{API_BASE_URL}/admin/prompts/",
                    json=test_prompt,
                    timeout=10
                )
                
                if response.status_code == 200:
                    created_prompt = response.json()
                    print(f"  ✅ Created: {created_prompt['name']} (v{created_prompt['version']})")
                else:
                    print(f"  ❌ Failed to create prompt: {response.text}")
                    return False
        else:
            print(f"  ❌ Failed to check prompts: {response.text}")
            return False
    except Exception as e:
        print(f"  ❌ Prompt check error: {e}")
        return False
    
    # Step 3: Verify setup
    print("\n✅ Verifying Setup:")
    try:
        # Check AI configurations
        response = requests.get(f"{API_BASE_URL}/admin/ai-configurations/", timeout=10)
        if response.status_code == 200:
            configs = response.json()
            active_configs = [c for c in configs if c.get('is_active')]
            print(f"  ✅ Active AI configurations: {len(active_configs)}")
            for config in active_configs:
                print(f"    - {config['name']} ({config['provider']}/{config['model']})")
        
        # Check prompts
        response = requests.get(f"{API_BASE_URL}/admin/prompts/", timeout=10)
        if response.status_code == 200:
            prompts = response.json()
            active_prompts = [p for p in prompts if p.get('status') == 'active']
            print(f"  ✅ Active prompts: {len(active_prompts)}")
            for prompt in active_prompts:
                print(f"    - {prompt['name']} (v{prompt['version']})")
        
    except Exception as e:
        print(f"  ❌ Verification error: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎯 Setup Complete!")
    print("  ✅ AI Configuration: Created and activated")
    print("  ✅ Active Prompt: Available")
    print("  ✅ Pipeline: Ready for testing")
    
    print("\n💡 Next Steps:")
    print("  1. Run: python test_ai_pipeline.py")
    print("  2. Test the AI analysis functionality")
    print("  3. Verify the complete pipeline")
    
    return True

if __name__ == "__main__":
    success = setup_ai_pipeline()
    if success:
        print("\n🎉 Setup: SUCCESS")
    else:
        print("\n❌ Setup: FAILED")
