#!/usr/bin/env python3
"""
Show ALL reports with pagination.
"""

import requests
import json
from datetime import datetime

BASE_URL = 'https://v2asbest-tool-production.up.railway.app'

def show_all_reports():
    """Show all reports with pagination."""
    
    print("🔍 SHOWING ALL REPORTS (WITH PAGINATION)")
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
    
    all_reports = []
    page = 1
    page_size = 100  # Get more per page
    
    while True:
        # Get reports with pagination
        response = requests.get(f"{BASE_URL}/reports/?page={page}&page_size={page_size}", headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Failed to get reports page {page}: {response.status_code}")
            break
        
        data = response.json()
        reports = data.get('items', [])
        total = data.get('total', 0)
        
        if not reports:
            break
            
        all_reports.extend(reports)
        print(f"📄 Page {page}: {len(reports)} reports (Total so far: {len(all_reports)}/{total})")
        
        if len(all_reports) >= total:
            break
            
        page += 1
    
    print(f"\n📊 FINAL TOTAL: {len(all_reports)} reports")
    print("=" * 80)
    
    for i, report in enumerate(all_reports, 1):
        print(f"\n{i:2d}. 📄 {report.get('filename', 'Unknown')}")
        print(f"    ID: {report.get('id', 'Unknown')}")
        print(f"    Status: {report.get('status', 'Unknown')}")
        print(f"    Score: {report.get('score', 'N/A')}")
        print(f"    Findings: {report.get('finding_count', 0)}")
        print(f"    Uploaded: {report.get('uploaded_at', 'Unknown')}")
        print(f"    Tenant: {report.get('tenant_name', 'N/A')}")
        print("-" * 60)
    
    print(f"\n🎉 Total: {len(all_reports)} reports displayed")

if __name__ == "__main__":
    show_all_reports()
