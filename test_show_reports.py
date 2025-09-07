#!/usr/bin/env python3
"""
Show all 38 reports with details.
"""

import requests
import json
from datetime import datetime

BASE_URL = 'https://v2asbest-tool-production.up.railway.app'

def show_reports():
    """Show all reports with details."""
    
    print("🔍 SHOWING ALL REPORTS")
    print("=" * 80)
    
    # Login
    response = requests.post(f"{BASE_URL}/auth/jwt/login", data={
        "username": "admin@bedrijfy.nl",
        "password": "Admin123!"
    })
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code}")
        return
    
    token = response.json().get('access_token')
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get reports
    response = requests.get(f"{BASE_URL}/reports/", headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Failed to get reports: {response.status_code}")
        return
    
    data = response.json()
    reports = data.get('items', [])
    total = data.get('total', 0)
    
    print(f"📊 Total Reports: {total}")
    print("=" * 80)
    
    for i, report in enumerate(reports, 1):
        print(f"\n{i:2d}. 📄 {report.get('filename', 'Unknown')}")
        print(f"    ID: {report.get('id', 'Unknown')}")
        print(f"    Status: {report.get('status', 'Unknown')}")
        print(f"    Score: {report.get('score', 'N/A')}")
        print(f"    Findings: {report.get('finding_count', 0)}")
        print(f"    Uploaded: {report.get('uploaded_at', 'Unknown')}")
        print(f"    Tenant: {report.get('tenant_name', 'N/A')}")
        print("-" * 60)
    
    print(f"\n🎉 Total: {len(reports)} reports displayed")

if __name__ == "__main__":
    show_reports()
