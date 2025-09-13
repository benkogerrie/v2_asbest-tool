#!/usr/bin/env python3
"""
Check welke prompts actief zijn
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
            return None
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def check_all_prompts(token):
    """Check alle prompts en hun status"""
    print("📝 Alle Prompts Check")
    print("=" * 50)
    
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f"{API_BASE_URL}/admin/prompts/", headers=headers)
        
        if response.status_code == 200:
            prompts = response.json()
            print(f"Totaal aantal prompts: {len(prompts)}")
            print()
            
            # Group by name and status
            by_name = {}
            for prompt in prompts:
                name = prompt.get('name', 'Unknown')
                if name not in by_name:
                    by_name[name] = []
                by_name[name].append(prompt)
            
            for name, prompt_list in by_name.items():
                print(f"📋 {name}:")
                for prompt in prompt_list:
                    status = prompt.get('status', 'Unknown')
                    version = prompt.get('version', 'Unknown')
                    print(f"   Versie {version}: {status}")
                print()
            
            # Check for active analysis_v1
            analysis_prompts = by_name.get('analysis_v1', [])
            active_analysis = [p for p in analysis_prompts if p.get('status') == 'active']
            
            if active_analysis:
                print("✅ Actieve analysis_v1 prompt gevonden!")
                return active_analysis[0]
            else:
                print("❌ Geen actieve analysis_v1 prompt!")
                print("💡 Oplossing: Maak een prompt actief via de UI")
                return None
                
        else:
            print(f"❌ Prompts failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Prompts check failed: {e}")
        return None

def check_ai_config(token):
    """Check AI configuratie"""
    print("\n🔧 AI Configuratie Check")
    print("-" * 30)
    
    try:
        headers = {'Authorization': f'Bearer {token}'}
        
        # Try to get AI config
        response = requests.get(f"{API_BASE_URL}/admin/ai-config/", headers=headers)
        print(f"AI Config endpoint: {response.status_code}")
        
        if response.status_code == 200:
            config = response.json()
            print("✅ AI Config gevonden:")
            print(f"   Provider: {config.get('provider', 'Unknown')}")
            print(f"   Model: {config.get('model', 'Unknown')}")
            print(f"   API Key: {'***' + config.get('api_key', '')[-4:] if config.get('api_key') else 'NIET GECONFIGUREERD'}")
            return config
        else:
            print("❌ AI Config niet beschikbaar")
            return None
            
    except Exception as e:
        print(f"❌ AI Config check failed: {e}")
        return None

def main():
    print("🚀 Actieve Prompts & AI Config Check")
    print("=" * 50)
    
    # Login
    token = login()
    if not token:
        print("❌ Login mislukt")
        return
    
    # Check prompts
    active_prompt = check_all_prompts(token)
    
    # Check AI config
    ai_config = check_ai_config(token)
    
    print("\n" + "=" * 50)
    print("📋 SAMENVATTING:")
    print(f"   Actieve analysis_v1 prompt: {'✅ JA' if active_prompt else '❌ NEE'}")
    print(f"   AI Configuratie: {'✅ OK' if ai_config else '❌ PROBLEEM'}")
    
    if not active_prompt:
        print("\n💡 OPLOSSING:")
        print("   1. Ga naar de System Owner UI")
        print("   2. Ga naar Prompts sectie")
        print("   3. Maak een analysis_v1 prompt actief")
        print("   4. Test opnieuw")

if __name__ == "__main__":
    main()


