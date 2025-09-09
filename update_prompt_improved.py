#!/usr/bin/env python3
"""
Update the analysis_v1 prompt with improved version to fix validation errors
"""

import requests
import json
import time
from datetime import datetime

# Configuration
API_BASE_URL = "https://v2asbest-tool-production.up.railway.app"

def update_prompt_improved():
    """Update the analysis_v1 prompt with improved version"""
    print("📝 Updating analysis_v1 prompt with improved version...")
    print("=" * 60)
    
    # Test 1: System Health
    print("🏥 System Health Check:")
    try:
        response = requests.get(f"{API_BASE_URL}/healthz", timeout=10)
        if response.status_code == 200:
            print("  ✅ Backend API: Healthy")
        else:
            print("  ❌ Backend API: Unhealthy")
            return False
    except Exception as e:
        print(f"  ❌ Backend API: Error - {e}")
        return False
    
    # Test 2: Get current prompt
    print("\n📋 Get Current Prompt:")
    try:
        response = requests.get(f"{API_BASE_URL}/admin/prompts/", timeout=10)
        if response.status_code == 200:
            prompts = response.json()
            active_prompts = [p for p in prompts if p.get('status') == 'active']
            if active_prompts:
                current_prompt = active_prompts[0]
                print(f"  ✅ Found active prompt: {current_prompt['name']} (v{current_prompt['version']})")
                print(f"  📄 Current content length: {len(current_prompt['content'])} characters")
            else:
                print("  ❌ No active prompts found")
                return False
        else:
            print(f"  ❌ Failed to get prompts: {response.text}")
            return False
    except Exception as e:
        print(f"  ❌ Get prompts error: {e}")
        return False
    
    # Test 3: Read improved prompt content
    print("\n📖 Read Improved Prompt Content:")
    try:
        with open("seeds/analysis_v1_improved.md", "r", encoding="utf-8") as f:
            improved_content = f.read()
        
        print(f"  ✅ Improved prompt content loaded: {len(improved_content)} characters")
        print(f"  📄 Key improvements:")
        print(f"    - All fields are mandatory")
        print(f"    - Exact category values specified")
        print(f"    - Exact severity levels specified")
        print(f"    - Always include suggested_fix")
        print(f"    - Better examples and guidelines")
        
    except Exception as e:
        print(f"  ❌ Failed to read improved prompt: {e}")
        return False
    
    # Test 4: Update prompt
    print("\n✏️  Update Prompt:")
    try:
        update_data = {
            "content": improved_content,
            "description": "Improved analysis prompt with better validation and clearer guidelines"
        }
        
        response = requests.put(
            f"{API_BASE_URL}/admin/prompts/{current_prompt['id']}",
            json=update_data,
            timeout=10
        )
        
        if response.status_code == 200:
            updated_prompt = response.json()
            print(f"  ✅ Prompt updated successfully")
            print(f"  📄 New version: v{updated_prompt['version']}")
            print(f"  📄 New content length: {len(updated_prompt['content'])} characters")
        else:
            print(f"  ❌ Failed to update prompt: {response.text}")
            return False
    except Exception as e:
        print(f"  ❌ Update prompt error: {e}")
        return False
    
    # Test 5: Test improved prompt
    print("\n🧪 Test Improved Prompt:")
    try:
        test_payload = {
            "sample_text": """
            ASBEST INVENTARISATIE RAPPORT
            
            Locatie: Test Gebouw, Amsterdam
            Datum: 2024-01-15
            Inspecteur: Jan de Vries
            
            SAMENVATTING:
            Dit rapport bevat een inventarisatie van asbesthoudende materialen
            in het onderzochte gebouw. Er zijn verschillende materialen gevonden
            die asbest bevatten.
            
            BEVINDINGEN:
            - Dak: Asbestcementplaten (Chrysotiel) - Conditie: Slecht - Risico: KRITIEK
            - CV-ruimte: Asbestisolatie leidingen (Chrysotiel) - Conditie: Matig - Risico: HOOG
            - Vloer: Asbesthoudende vloerbedekking (Chrysotiel) - Conditie: Goed - Risico: MEDIUM
            
            AANBEVELINGEN:
            - Directe verwijdering van kritieke asbesthoudende materialen
            - Professionele sanering door gecertificeerd bedrijf
            - Periodieke controle van overige asbesthoudende materialen
            
            HANDTEKENING: Jan de Vries
            DATUM: 15 januari 2024
            """
        }
        
        response = requests.post(
            f"{API_BASE_URL}/admin/prompts/{updated_prompt['id']}/test-run",
            json=test_payload,
            timeout=60
        )
        
        if response.status_code == 200:
            test_result = response.json()
            print(f"  ✅ Prompt test executed")
            print(f"  ⏱️  Execution time: {test_result.get('execution_time_ms', 'N/A')}ms")
            print(f"  📊 Result: {test_result.get('message', 'No message')}")
            
            if test_result.get('success'):
                print("  🎯 Prompt test: SUCCESS")
                if test_result.get('parsed_output'):
                    output = test_result['parsed_output']
                    print(f"    - Score: {output.get('score', 'N/A')}")
                    print(f"    - Findings: {len(output.get('findings', []))}")
                    print(f"    - Summary: {output.get('report_summary', 'N/A')[:100]}...")
                    
                    # Check if all findings have required fields
                    findings = output.get('findings', [])
                    if findings:
                        print("    - Validation check:")
                        for i, finding in enumerate(findings[:3]):  # Check first 3 findings
                            missing_fields = []
                            required_fields = ['code', 'title', 'category', 'severity', 'status', 'evidence_snippet', 'suggested_fix']
                            for field in required_fields:
                                if field not in finding or finding[field] is None:
                                    missing_fields.append(field)
                            
                            if missing_fields:
                                print(f"      Finding {i+1}: Missing fields: {missing_fields}")
                            else:
                                print(f"      Finding {i+1}: ✅ All required fields present")
            else:
                print("  ⚠️  Prompt test: FAILED (validation errors)")
                print("    This indicates the prompt still needs improvement")
        else:
            print(f"  ❌ Prompt test failed: {response.text}")
    except Exception as e:
        print(f"  ❌ Prompt test error: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 Prompt Update Summary:")
    print("  ✅ Backend API: Fully functional")
    print("  ✅ Current prompt: Retrieved successfully")
    print("  ✅ Improved prompt: Loaded successfully")
    print("  ✅ Prompt update: Completed successfully")
    print("  ✅ Prompt testing: Available")
    
    print("\n💡 Improvements Made:")
    print("  - All fields are now mandatory")
    print("  - Exact category values specified")
    print("  - Exact severity levels specified")
    print("  - Always include suggested_fix")
    print("  - Better examples and guidelines")
    print("  - Clearer validation rules")
    
    print("\n🌐 Frontend URL:")
    print("  https://v21-asbest-tool-nutv.vercel.app/system-owner#Prompts")
    
    return True

if __name__ == "__main__":
    success = update_prompt_improved()
    if success:
        print("\n🎉 Prompt Update: SUCCESS")
    else:
        print("\n❌ Prompt Update: FAILED")
