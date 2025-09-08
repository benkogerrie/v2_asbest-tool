#!/usr/bin/env python3
"""
Debug script voor Mixed Content probleem
Onderzoekt alle mogelijke oorzaken van HTTP vs HTTPS requests
"""

import requests
import json
import sys
from urllib.parse import urlparse

def test_railway_endpoints():
    """Test Railway endpoints voor HTTP/HTTPS redirects"""
    print("🔍 Testing Railway endpoints for HTTP/HTTPS redirects...")
    
    base_url = "v2asbest-tool-production.up.railway.app"
    endpoints = [
        "/healthz",
        "/admin/prompts",
        "/"
    ]
    
    for endpoint in endpoints:
        print(f"\n--- Testing {endpoint} ---")
        
        # Test HTTP
        http_url = f"http://{base_url}{endpoint}"
        try:
            print(f"HTTP Request: {http_url}")
            response = requests.get(http_url, allow_redirects=True, timeout=10)
            print(f"  Status: {response.status_code}")
            print(f"  Final URL: {response.url}")
            print(f"  Redirects: {len(response.history)}")
            for i, redirect in enumerate(response.history):
                print(f"    Redirect {i+1}: {redirect.status_code} -> {redirect.url}")
        except Exception as e:
            print(f"  HTTP Error: {e}")
        
        # Test HTTPS
        https_url = f"https://{base_url}{endpoint}"
        try:
            print(f"HTTPS Request: {https_url}")
            response = requests.get(https_url, allow_redirects=True, timeout=10)
            print(f"  Status: {response.status_code}")
            print(f"  Final URL: {response.url}")
            print(f"  Redirects: {len(response.history)}")
            for i, redirect in enumerate(response.history):
                print(f"    Redirect {i+1}: {redirect.status_code} -> {redirect.url}")
        except Exception as e:
            print(f"  HTTPS Error: {e}")

def test_cors_headers():
    """Test CORS headers van Railway"""
    print("\n🔍 Testing CORS headers...")
    
    base_url = "https://v2asbest-tool-production.up.railway.app"
    
    try:
        response = requests.options(f"{base_url}/admin/prompts", timeout=10)
        print(f"OPTIONS Request Status: {response.status_code}")
        print("CORS Headers:")
        for header, value in response.headers.items():
            if 'cors' in header.lower() or 'access-control' in header.lower():
                print(f"  {header}: {value}")
    except Exception as e:
        print(f"CORS Test Error: {e}")

def test_ssl_certificate():
    """Test SSL certificate van Railway"""
    print("\n🔍 Testing SSL certificate...")
    
    import ssl
    import socket
    
    hostname = "v2asbest-tool-production.up.railway.app"
    port = 443
    
    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                print(f"SSL Certificate valid for: {cert.get('subject', 'Unknown')}")
                print(f"SSL Certificate issuer: {cert.get('issuer', 'Unknown')}")
                print(f"SSL Certificate version: {cert.get('version', 'Unknown')}")
    except Exception as e:
        print(f"SSL Test Error: {e}")

def test_railway_environment():
    """Test Railway environment variables"""
    print("\n🔍 Testing Railway environment...")
    
    base_url = "https://v2asbest-tool-production.up.railway.app"
    
    try:
        response = requests.get(f"{base_url}/healthz", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("Health check response:")
            print(json.dumps(data, indent=2))
        else:
            print(f"Health check failed: {response.status_code}")
    except Exception as e:
        print(f"Environment Test Error: {e}")

def test_browser_simulation():
    """Simuleer browser requests"""
    print("\n🔍 Testing browser-like requests...")
    
    base_url = "https://v2asbest-tool-production.up.railway.app"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'nl-NL,nl;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Origin': 'https://v21-asbest-tool-nutv.vercel.app',
        'Referer': 'https://v21-asbest-tool-nutv.vercel.app/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site'
    }
    
    try:
        response = requests.get(f"{base_url}/admin/prompts", headers=headers, timeout=10)
        print(f"Browser-like request status: {response.status_code}")
        print(f"Response headers:")
        for header, value in response.headers.items():
            print(f"  {header}: {value}")
    except Exception as e:
        print(f"Browser Simulation Error: {e}")

def analyze_vercel_config():
    """Analyseer Vercel configuratie"""
    print("\n🔍 Analyzing Vercel configuration...")
    
    try:
        with open('vercel.json', 'r') as f:
            vercel_config = json.load(f)
            print("Vercel configuration:")
            print(json.dumps(vercel_config, indent=2))
    except FileNotFoundError:
        print("vercel.json not found")
    except Exception as e:
        print(f"Vercel config error: {e}")

def main():
    """Main debug function"""
    print("🚀 Starting Mixed Content Debug Analysis")
    print("=" * 50)
    
    test_railway_endpoints()
    test_cors_headers()
    test_ssl_certificate()
    test_railway_environment()
    test_browser_simulation()
    analyze_vercel_config()
    
    print("\n" + "=" * 50)
    print("✅ Debug analysis completed")

if __name__ == "__main__":
    main()
