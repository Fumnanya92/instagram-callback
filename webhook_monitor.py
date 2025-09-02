#!/usr/bin/env python3
"""
Real-time webhook monitor to see Meta verification attempts.
Run this while setting up webhooks in Meta Console.
"""

import requests
import time
import json
from datetime import datetime

def monitor_webhook_logs():
    """Monitor webhook logs in real-time."""
    
    print("🔍 Monitoring webhook activity...")
    print("💡 Keep this running while configuring webhooks in Meta Console")
    print("⏹️  Press Ctrl+C to stop\n")
    
    last_check = datetime.now()
    
    try:
        while True:
            try:
                # Check webhook logs
                response = requests.get("https://fynko.space/webhook/logs", timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    webhook_events = data.get("webhook_events", [])
                    
                    # Look for recent events
                    recent_events = []
                    for event in webhook_events:
                        try:
                            # Handle different timestamp formats
                            timestamp_str = event["timestamp"].replace("Z", "+00:00")
                            event_time = datetime.fromisoformat(timestamp_str)
                            # Make last_check timezone aware for comparison
                            if event_time.timestamp() > last_check.timestamp():
                                recent_events.append(event)
                        except (ValueError, KeyError):
                            # Skip events with invalid timestamps
                            continue
                    
                    if recent_events:
                        print(f"📡 New webhook activity detected:")
                        for event in recent_events:
                            print(f"   ⏰ {event['timestamp']}")
                            print(f"   📋 Event: {event['event']}")
                            if "data" in event:
                                print(f"   📄 Data: {json.dumps(event['data'], indent=6)}")
                            print()
                        
                        last_check = datetime.now()
                    else:
                        print("⏳ Waiting for webhook activity...", end="\r")
                
                else:
                    print(f"❌ Failed to check logs: {response.status_code}")
                
            except requests.exceptions.RequestException as e:
                print(f"⚠️  Connection issue: {e}")
            
            time.sleep(2)  # Check every 2 seconds
            
    except KeyboardInterrupt:
        print(f"\n\n✅ Monitoring stopped")

def test_webhook_now():
    """Send a test verification request right now."""
    
    print("🧪 Sending test verification request...")
    
    url = "https://fynko.space/webhook"
    params = {
        "hub.mode": "subscribe",
        "hub.verify_token": "grace_webhook_token", 
        "hub.challenge": f"test_from_monitor_{int(time.time())}"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        print(f"📊 Test Result:")
        print(f"   Status: {response.status_code}")
        print(f"   Response: '{response.text}'")
        print(f"   Expected: '{params['hub.challenge']}'")
        
        if response.status_code == 200 and response.text == params["hub.challenge"]:
            print("✅ Test verification successful!")
        else:
            print("❌ Test verification failed!")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    print("🚀 Webhook Real-Time Monitor\n")
    
    # Test webhook first
    test_webhook_now()
    print()
    
    # Ask what to do
    choice = input("What would you like to do?\n1. Monitor webhook logs in real-time\n2. Exit\nChoice (1/2): ").strip()
    
    if choice == "1":
        print()
        monitor_webhook_logs()
    else:
        print("👋 Goodbye!")
