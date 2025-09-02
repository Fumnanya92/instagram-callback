#!/usr/bin/env python3
"""
Real-time webhook testing tool.
This sends test webhooks to your deployed app and shows you the responses.
"""

import requests
import json
import time
from datetime import datetime

def test_webhook_verification():
    """Test webhook verification and show the response."""
    
    print("🔐 Testing Webhook Verification...")
    print("-" * 50)
    
    url = "https://fynko.space/webhook"
    params = {
        "hub.mode": "subscribe",
        "hub.verify_token": "grace_webhook_token",
        "hub.challenge": f"test_challenge_{int(time.time())}"
    }
    
    print(f"📤 Sending GET request to: {url}")
    print(f"📋 Parameters: {params}")
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        print(f"\n📊 Response:")
        print(f"   Status: {response.status_code}")
        print(f"   Body: '{response.text}'")
        print(f"   Expected: '{params['hub.challenge']}'")
        
        if response.status_code == 200 and response.text == params["hub.challenge"]:
            print("✅ Verification SUCCESS!")
        else:
            print("❌ Verification FAILED!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n")

def test_message_webhook():
    """Test sending a message webhook."""
    
    print("💬 Testing Message Webhook...")
    print("-" * 50)
    
    url = "https://fynko.space/webhook"
    
    # Test payload that matches Meta's structure
    payload = {
        "object": "instagram",
        "entry": [
            {
                "id": "17841457603940745",  # Your Instagram account ID
                "time": int(time.time()),
                "messaging": [
                    {
                        "sender": {"id": "test_user_12345"},
                        "recipient": {"id": "17841457603940745"},
                        "timestamp": int(time.time()),
                        "message": {
                            "mid": f"test_message_{int(time.time())}",
                            "text": "Hello! This is a test message to see backend logging."
                        }
                    }
                ]
            }
        ]
    }
    
    print(f"📤 Sending POST request to: {url}")
    print(f"📋 Payload:")
    print(json.dumps(payload, indent=2))
    
    try:
        response = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"\n📊 Response:")
        print(f"   Status: {response.status_code}")
        print(f"   Body: {response.text}")
        
        if response.status_code == 200:
            print("✅ Message webhook SUCCESS!")
            
            # Check logs
            print("\n📋 Checking webhook logs...")
            logs_response = requests.get("https://fynko.space/webhook/logs")
            if logs_response.status_code == 200:
                logs = logs_response.json()
                webhook_events = logs.get("webhook_events", [])
                auto_replies = logs.get("auto_replies", [])
                
                print(f"   📝 Total webhook events: {len(webhook_events)}")
                print(f"   💬 Total auto-replies: {len(auto_replies)}")
                
                # Show latest events
                if webhook_events:
                    latest = webhook_events[-1]
                    print(f"   🕐 Latest event: {latest.get('timestamp', 'N/A')}")
                
                if auto_replies:
                    latest_reply = auto_replies[-1]
                    print(f"   🤖 Latest reply to: {latest_reply.get('sender_id', 'N/A')}")
                    print(f"   📝 Reply status: {latest_reply.get('status', 'N/A')}")
        else:
            print("❌ Message webhook FAILED!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n")

def show_current_logs():
    """Show current webhook logs."""
    
    print("📋 Current Webhook Logs...")
    print("-" * 50)
    
    try:
        response = requests.get("https://fynko.space/webhook/logs")
        
        if response.status_code == 200:
            data = response.json()
            webhook_events = data.get("webhook_events", [])
            auto_replies = data.get("auto_replies", [])
            
            print(f"📝 Webhook Events ({len(webhook_events)} total):")
            for i, event in enumerate(webhook_events[-3:], 1):  # Show last 3
                print(f"   {i}. {event.get('timestamp', 'N/A')} - {event.get('event', 'N/A')}")
            
            print(f"\n💬 Auto-Replies ({len(auto_replies)} total):")
            for i, reply in enumerate(auto_replies[-3:], 1):  # Show last 3
                print(f"   {i}. {reply.get('timestamp', 'N/A')} - To: {reply.get('sender_id', 'N/A')} - Status: {reply.get('status', 'N/A')}")
                
        else:
            print(f"❌ Failed to get logs: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n")

if __name__ == "__main__":
    print("🚀 Webhook Testing & Monitoring Tool")
    print("=" * 60)
    print()
    
    while True:
        print("What would you like to do?")
        print("1. Test webhook verification")
        print("2. Test message webhook")
        print("3. Show current logs")
        print("4. Exit")
        
        choice = input("\nChoice (1-4): ").strip()
        
        if choice == "1":
            test_webhook_verification()
        elif choice == "2":
            test_message_webhook()
        elif choice == "3":
            show_current_logs()
        elif choice == "4":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.\n")
