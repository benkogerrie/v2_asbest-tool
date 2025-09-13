#!/usr/bin/env python3
"""
Test prompts en AI analyse op Railway
"""
import requests
import json

# API Configuration
API_BASE_URL = "https://v2asbest-tool-production.up.railway.app"

def login():
    """Login en krijg JWT token"""
    login_data = {
        "username": "admin@bedrijfy.nl",
        "password": "Admin123!"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/jwt/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get('access_token')
        else:
            print(f"❌ Login mislukt: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_prompts(token):
    """Test prompts"""
    print("📝 Prompts Test")
    print("-" * 30)
    
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f"{API_BASE_URL}/admin/prompts/", headers=headers)
        
        if response.status_code == 200:
            prompts = response.json()
            print(f"✅ Aantal prompts: {len(prompts)}")
            
            # Find analysis_v1 prompt
            analysis_prompt = None
            for prompt in prompts:
                if prompt.get('name') == 'analysis_v1':
                    analysis_prompt = prompt
                    break
            
            if analysis_prompt:
                print(f"✅ analysis_v1 prompt gevonden:")
                print(f"   ID: {analysis_prompt.get('id')}")
                print(f"   Status: {analysis_prompt.get('status')}")
                print(f"   Versie: {analysis_prompt.get('version')}")
                print(f"   Content lengte: {len(analysis_prompt.get('content', ''))}")
                return analysis_prompt
            else:
                print("❌ analysis_v1 prompt niet gevonden!")
                return None
        else:
            print(f"❌ Prompts failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Prompts test failed: {e}")
        return None

def test_prompt_test_run(token, prompt_id):
    """Test prompt test-run endpoint"""
    print("\n🧪 Prompt Test-Run")
    print("-" * 30)
    
    try:
        headers = {'Authorization': f'Bearer {token}'}
        
        # Test data
        test_data = {
            "sample_text": "Dit is een test asbest rapport. Het rapport bevat alle vereiste informatie volgens artikel 22.",
            "checklist": "Test checklist",
            "severity_weights": {"CRITICAL": 30, "HIGH": 15, "MEDIUM": 7, "LOW": 3},
            "output_schema": "Test schema"
        }
        
        response = requests.post(
            f"{API_BASE_URL}/admin/prompts/{prompt_id}/test-run",
            json=test_data,
            headers=headers,
            timeout=60
        )
        
        print(f"Test-run response: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Prompt test-run succesvol!")
            print(f"   Raw output: {result.get('raw_output', '')[:200]}...")
            return True
        else:
            print(f"❌ Prompt test-run failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Prompt test-run error: {e}")
        return False

def main():
    print("🚀 Prompts & AI Analyse Test")
    print("=" * 50)
    
    # Login
    token = login()
    if not token:
        return
    
    # Test prompts
    analysis_prompt = test_prompts(token)
    if not analysis_prompt:
        return
    
    # Test prompt test-run
    test_run_ok = test_prompt_test_run(token, analysis_prompt.get('id'))
    
    print("\n" + "=" * 50)
    print("📋 RESULTATEN:")
    print(f"   Prompts: {'✅ OK' if analysis_prompt else '❌ FAILED'}")
    print(f"   Test-Run: {'✅ OK' if test_run_ok else '❌ FAILED'}")
    
    if test_run_ok:
        print("\n🎉 AI analyse zou moeten werken!")
        print("💡 Het probleem ligt waarschijnlijk in de worker pipeline")
    else:
        print("\n❌ AI analyse werkt niet - API key probleem!")

if __name__ == "__main__":
    main()


