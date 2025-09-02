#!/usr/bin/env python3
"""
Test webhook message handling with the actual data structure Meta sends.
"""

import requests
import json

def test_message_webhook():
    """Send a test message webhook to see the full flow."""
    
    # This is the structure Meta actually sends for Instagram messages
    test_payload = {
        "object": "instagram",
        "entry": [
            {
                "id": "17841457603940745",  # Your Instagram account ID
                "time": 1756828500,
                "messaging": [
                    {
                        "sender": {"id": "test_user_123"},
                        "recipient": {"id": "17841457603940745"},
                        "timestamp": 1756828500,
                        "message": {
                            "mid": "test_message_id_456",
                            "text": "Hello! I'm interested in your services."
                        }
                    }
                ]
            }
        ]
    }
    
    print("🧪 Testing message webhook handler...")
    print(f"📤 Sending test message payload to webhook...")
    
    try:
        response = requests.post(
            "https://fynko.space/webhook",
            json=test_payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📄 Response Body: {response.text}")
        
        if response.status_code == 200:
            print("✅ Webhook message handling successful!")
            
            # Check if auto-reply was logged
            print("\n🔍 Checking for auto-reply in logs...")
            logs_response = requests.get("https://fynko.space/webhook/logs")
            if logs_response.status_code == 200:
                logs = logs_response.json()
                auto_replies = logs.get("auto_replies", [])
                recent_replies = [r for r in auto_replies if "test_user_123" in str(r)]
                
                if recent_replies:
                    print("✅ Auto-reply generated!")
                    print(json.dumps(recent_replies[-1], indent=2))
                else:
                    print("⚠️  No auto-reply found (check PAGE_ACCESS_TOKEN configuration)")
        else:
            print("❌ Webhook message handling failed!")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_message_webhook()
