#!/usr/bin/env python3
"""
Activate analysis_v1 prompt automatically
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
            print(f"❌ System owner login mislukt: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def find_analysis_prompt(token):
    """Vind de analysis_v1 prompt"""
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f"{API_BASE_URL}/admin/prompts/", headers=headers)
        
        if response.status_code == 200:
            prompts = response.json()
            
            # Find analysis_v1 version 2
            for prompt in prompts:
                if (prompt.get('name') == 'analysis_v1' and 
                    prompt.get('version') == 2):
                    return prompt
            
            return None
        else:
            print(f"❌ Prompts failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Find prompt failed: {e}")
        return None

def activate_prompt(token, prompt_id):
    """Activeer een prompt"""
    try:
        headers = {'Authorization': f'Bearer {token}'}
        
        # Update prompt status to active
        update_data = {"status": "active"}
        
        response = requests.put(
            f"{API_BASE_URL}/admin/prompts/{prompt_id}",
            json=update_data,
            headers=headers,
            timeout=30
        )
        
        print(f"Activate response: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Prompt geactiveerd!")
            return True
        else:
            print(f"❌ Activate failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Activate error: {e}")
        return False

def main():
    print("🚀 Analysis Prompt Activator")
    print("=" * 50)
    
    # Login als system owner
    token = login_system_owner()
    if not token:
        return
    
    # Vind analysis_v1 prompt
    prompt = find_analysis_prompt(token)
    if not prompt:
        print("❌ analysis_v1 prompt (versie 2) niet gevonden!")
        return
    
    print(f"✅ analysis_v1 prompt gevonden:")
    print(f"   ID: {prompt.get('id')}")
    print(f"   Status: {prompt.get('status')}")
    print(f"   Versie: {prompt.get('version')}")
    
    # Activeer prompt
    if activate_prompt(token, prompt.get('id')):
        print("\n🎉 analysis_v1 prompt is nu actief!")
        print("💡 AI analyse zou nu moeten werken")
    else:
        print("\n❌ Kon prompt niet activeren")

if __name__ == "__main__":
    main()

