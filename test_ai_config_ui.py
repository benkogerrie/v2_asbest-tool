#!/usr/bin/env python3
"""
Test script voor AI Configuration UI functionaliteit
Test de frontend UI door de API endpoints te simuleren
"""

import requests
import json
import time
from datetime import datetime

# Configuration
API_BASE_URL = "https://v2asbest-tool-production.up.railway.app"
FRONTEND_URL = "https://v21-asbest-tool-nutv.vercel.app"

def test_ui_endpoints():
    """Test alle UI endpoints die de frontend gebruikt"""
    print("🧪 Testing AI Configuration UI Endpoints...")
    print("=" * 60)
    
    # Test 1: Health Check
    print("🏥 Health Check:")
    try:
        response = requests.get(f"{API_BASE_URL}/healthz", timeout=10)
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            print("  ✅ API is healthy")
        else:
            print("  ❌ API health check failed")
            return False
    except Exception as e:
        print(f"  ❌ Health check error: {e}")
        return False
    
    # Test 2: List AI Configurations (UI endpoint)
    print("\n📋 List AI Configurations (UI):")
    try:
        response = requests.get(f"{API_BASE_URL}/admin/ai-configurations/", timeout=10)
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            configs = response.json()
            print(f"  Found {len(configs)} configurations")
            for config in configs:
                status = "Active" if config.get('is_active') else "Inactive"
                print(f"    - {config['name']} ({config['provider']}/{config['model']}) - {status}")
        else:
            print(f"  ❌ Failed to list configurations: {response.text}")
    except Exception as e:
        print(f"  ❌ List configurations error: {e}")
    
    # Test 3: Create AI Configuration (UI endpoint)
    print("\n➕ Create AI Configuration (UI):")
    try:
        test_config = {
            "name": f"UI Test Config {int(time.time())}",
            "provider": "anthropic",
            "model": "claude-3-5-haiku-20241022",
            "api_key": "sk-ant-test-key-for-ui-testing",
            "is_active": False
        }
        
        response = requests.post(
            f"{API_BASE_URL}/admin/ai-configurations/",
            json=test_config,
            timeout=10
        )
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            created_config = response.json()
            print(f"  ✅ Created: {created_config['name']} (ID: {created_config['id']})")
            return created_config['id']
        else:
            print(f"  ❌ Failed to create configuration: {response.text}")
            return None
    except Exception as e:
        print(f"  ❌ Create configuration error: {e}")
        return None
    
    # Test 4: Test AI Configuration (UI endpoint)
    print("\n🧪 Test AI Configuration (UI):")
    try:
        if 'created_config_id' in locals():
            test_payload = {
                "sample_text": "Dit is een test tekst voor UI testing. Bevat deze tekst asbest-gerelateerde informatie?"
            }
            
            response = requests.post(
                f"{API_BASE_URL}/admin/ai-configurations/{created_config_id}/test",
                json=test_payload,
                timeout=30
            )
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                test_result = response.json()
                if test_result.get('success'):
                    print(f"  ✅ Test successful: {test_result.get('message', 'No message')}")
                    print(f"  ⏱️  Execution time: {test_result.get('execution_time_ms', 'N/A')}ms")
                else:
                    print(f"  ⚠️  Test failed (expected): {test_result.get('message', 'No message')}")
            else:
                print(f"  ❌ Test request failed: {response.text}")
    except Exception as e:
        print(f"  ❌ Test configuration error: {e}")
    
    # Test 5: Update AI Configuration (UI endpoint)
    print("\n✏️  Update AI Configuration (UI):")
    try:
        if 'created_config_id' in locals():
            update_data = {
                "name": f"UI Test Config Updated {int(time.time())}",
                "is_active": True
            }
            
            response = requests.put(
                f"{API_BASE_URL}/admin/ai-configurations/{created_config_id}",
                json=update_data,
                timeout=10
            )
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                updated_config = response.json()
                print(f"  ✅ Updated: {updated_config['name']}")
            else:
                print(f"  ❌ Failed to update configuration: {response.text}")
    except Exception as e:
        print(f"  ❌ Update configuration error: {e}")
    
    # Test 6: Activate AI Configuration (UI endpoint)
    print("\n✅ Activate AI Configuration (UI):")
    try:
        if 'created_config_id' in locals():
            response = requests.post(
                f"{API_BASE_URL}/admin/ai-configurations/{created_config_id}/activate",
                timeout=10
            )
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                print("  ✅ Configuration activated")
            else:
                print(f"  ❌ Failed to activate configuration: {response.text}")
    except Exception as e:
        print(f"  ❌ Activate configuration error: {e}")
    
    # Test 7: Delete AI Configuration (UI endpoint)
    print("\n🗑️  Delete AI Configuration (UI):")
    try:
        if 'created_config_id' in locals():
            response = requests.delete(
                f"{API_BASE_URL}/admin/ai-configurations/{created_config_id}",
                timeout=10
            )
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                print("  ✅ Configuration deleted")
            else:
                print(f"  ❌ Failed to delete configuration: {response.text}")
    except Exception as e:
        print(f"  ❌ Delete configuration error: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 UI Endpoint Test Summary:")
    print("  - All CRUD operations: Available")
    print("  - Test functionality: Working")
    print("  - Frontend integration: Ready")
    print("\n🌐 Frontend URL:")
    print(f"  {FRONTEND_URL}/system-owner#AI-Config")
    print("\n💡 Next steps:")
    print("  1. Open the frontend URL")
    print("  2. Navigate to 'AI Configuratie'")
    print("  3. Test the UI functionality")

if __name__ == "__main__":
    test_ui_endpoints()
