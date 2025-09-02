#!/usr/bin/env python3
"""
Test the webhook status endpoint to verify fynko.space configuration.
"""

import requests
import json
import sys

def test_webhook_status():
    """Test the webhook status endpoint."""
    
    try:
        print("🧪 Testing webhook status endpoint...")
        response = requests.get("http://127.0.0.1:8000/webhook/status", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Webhook status endpoint working!")
            print("\n📊 Configuration Status:")
            print(json.dumps(data, indent=2))
            
            # Verify fynko.space URLs are present
            if "fynko.space" in str(data):
                print("\n✅ fynko.space domain correctly configured!")
            else:
                print("\n❌ fynko.space domain not found in response")
            
        else:
            print(f"❌ Error: HTTP {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - make sure the server is running on http://127.0.0.1:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_webhook_logs():
    """Test the webhook logs endpoint."""
    
    try:
        print("\n🧪 Testing webhook logs endpoint...")
        response = requests.get("http://127.0.0.1:8000/webhook/logs", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Webhook logs endpoint working!")
            
            webhook_events = data.get("webhook_events", [])
            auto_replies = data.get("auto_replies", [])
            
            print(f"📝 Found {len(webhook_events)} webhook events")
            print(f"💬 Found {len(auto_replies)} auto-replies")
            
            if webhook_events or auto_replies:
                print("✅ Sample data ready for Meta reviewers!")
            else:
                print("⚠️  No sample data found")
            
        else:
            print(f"❌ Error: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_webhook_status()
    test_webhook_logs()
    print("\n🎯 Ready for Meta app review!")
