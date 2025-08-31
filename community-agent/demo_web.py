#!/usr/bin/env python3
"""
Web Interface Demo for the Agentic Community Assistant

This script demonstrates that the web interface is working and accessible.
"""

import requests
import webbrowser
import time

def test_web_interface():
    """Test the web interface and open it in browser"""
    print("🌐 TESTING WEB INTERFACE")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Test if server is running
    try:
        print("1. Testing server health...")
        health_response = requests.get(f"{base_url}/health")
        if health_response.status_code == 200:
            print("✅ Server is healthy and running")
        else:
            print(f"❌ Server health check failed: {health_response.status_code}")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure it's running on port 8000")
        return
    
    # Test web interface
    try:
        print("2. Testing web interface...")
        web_response = requests.get(base_url)
        if web_response.status_code == 200:
            print("✅ Web interface is accessible")
            print(f"   - Response size: {len(web_response.text)} characters")
            print(f"   - Contains HTML: {'<!DOCTYPE html>' in web_response.text}")
            print(f"   - Contains title: {'Agentic Community Assistant' in web_response.text}")
        else:
            print(f"❌ Web interface failed: {web_response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error testing web interface: {e}")
        return
    
    # Test API endpoints
    try:
        print("3. Testing API endpoints...")
        api_response = requests.get(f"{base_url}/docs")
        if api_response.status_code == 200:
            print("✅ API documentation is accessible")
        else:
            print(f"⚠️  API docs failed: {api_response.status_code}")
    except Exception as e:
        print(f"⚠️  API docs test failed: {e}")
    
    # Open web interface
    print("\n4. Opening web interface in browser...")
    try:
        webbrowser.open(base_url)
        print("✅ Browser opened successfully")
    except Exception as e:
        print(f"⚠️  Could not open browser automatically: {e}")
        print(f"   Please open manually: {base_url}")
    
    print("\n" + "=" * 50)
    print("🎉 WEB INTERFACE DEMO COMPLETED!")
    print("=" * 50)
    print("What you should see:")
    print("✅ Beautiful, modern web interface")
    print("✅ User-friendly forms (not JSON API calls)")
    print("✅ Visual journey progress tracking")
    print("✅ Interactive step-by-step workflow")
    print("✅ Mobile-responsive design")
    print("✅ Professional government service look")
    
    print("\nUser Experience Features:")
    print("🚀 Simple 'Start My Journey' button")
    print("📝 Easy-to-fill forms with validation")
    print("🎯 Visual progress tracking")
    print("✅ Step-by-step guidance")
    print("🔒 Privacy and consent management")
    print("📱 Mobile-friendly design")
    
    print(f"\n🌐 Open your browser to: {base_url}")
    print("📚 API documentation: {base_url}/docs")

if __name__ == "__main__":
    test_web_interface()
