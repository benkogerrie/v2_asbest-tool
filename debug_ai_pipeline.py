#!/usr/bin/env python3
"""
Debug AI pipeline stap voor stap
"""
import requests
import json

# API Configuration
API_BASE_URL = "https://v2asbest-tool-production.up.railway.app"

def login_system_owner():
    """Login als system owner"""
    login_data = {
        "username": "system@asbest-tool.nl",
        "password": "SystemOwner123!"
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
            return None
    except:
        return None

def test_ai_config_endpoint(token):
    """Test AI config endpoints"""
    print("🔧 AI Config Endpoints Test")
    print("-" * 30)
    
    headers = {'Authorization': f'Bearer {token}'}
    
    endpoints = [
        "/admin/ai-config/",
        "/admin/ai-config",
        "/config/ai",
        "/debug/ai-config"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{API_BASE_URL}{endpoint}", headers=headers, timeout=10)
            print(f"   {endpoint}: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"      Data: {data}")
        except Exception as e:
            print(f"   {endpoint}: Error - {e}")

def test_prompt_test_run(token):
    """Test prompt test-run met actieve prompt"""
    print("\n🧪 Prompt Test-Run")
    print("-" * 30)
    
    try:
        headers = {'Authorization': f'Bearer {token}'}
        
        # Get active analysis_v1 prompt
        response = requests.get(f"{API_BASE_URL}/admin/prompts/", headers=headers)
        if response.status_code == 200:
            prompts = response.json()
            active_prompt = None
            for prompt in prompts:
                if (prompt.get('name') == 'analysis_v1' and 
                    prompt.get('status') == 'active'):
                    active_prompt = prompt
                    break
            
            if not active_prompt:
                print("❌ Geen actieve analysis_v1 prompt gevonden")
                return False
            
            print(f"✅ Actieve prompt gevonden: {active_prompt.get('id')}")
            
            # Test run
            test_data = {
                "sample_text": "Dit is een test asbest rapport met alle vereiste informatie.",
                "checklist": "Test checklist",
                "severity_weights": {"CRITICAL": 30, "HIGH": 15, "MEDIUM": 7, "LOW": 3},
                "output_schema": "Test schema"
            }
            
            response = requests.post(
                f"{API_BASE_URL}/admin/prompts/{active_prompt.get('id')}/test-run",
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
        print(f"❌ Prompt test error: {e}")
        return False

def check_worker_status():
    """Check worker status"""
    print("\n⚙️ Worker Status Check")
    print("-" * 30)
    
    try:
        # Check if there's a worker status endpoint
        response = requests.get(f"{API_BASE_URL}/worker/status", timeout=10)
        print(f"Worker status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Data: {data}")
        
        # Check queue status
        response = requests.get(f"{API_BASE_URL}/queue/status", timeout=10)
        print(f"Queue status: {response.status_code}")
        
    except Exception as e:
        print(f"Worker check error: {e}")

def main():
    print("🚀 AI Pipeline Debug")
    print("=" * 50)
    
    # Login
    token = login_system_owner()
    if not token:
        print("❌ System owner login mislukt")
        return
    
    # Test AI config
    test_ai_config_endpoint(token)
    
    # Test prompt test-run
    test_run_ok = test_prompt_test_run(token)
    
    # Check worker status
    check_worker_status()
    
    print("\n" + "=" * 50)
    print("📋 RESULTATEN:")
    print(f"   Prompt Test-Run: {'✅ OK' if test_run_ok else '❌ FAILED'}")
    
    if not test_run_ok:
        print("\n💡 MOGELIJKE OORZAKEN:")
        print("   1. AI_API_KEY niet geconfigureerd in Railway")
        print("   2. AI service niet beschikbaar")
        print("   3. Prompt content heeft problemen")
        print("   4. Worker heeft andere configuratie")

if __name__ == "__main__":
    main()

