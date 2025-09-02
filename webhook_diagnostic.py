#!/usr/bin/env python3
"""
Webhook diagnostic tool for Meta Instagram integration.
This helps troubleshoot webhook setup issues.
"""

import requests
import json
import time
from datetime import datetime

def test_webhook_verification():
    """Test the webhook verification endpoint manually."""
    
    print("🔍 Testing webhook verification endpoint...")
    
    # Test the GET endpoint that Meta will call for verification
    base_url = "https://fynko.space/webhook"  # Change this if testing locally
    
    # These are the parameters Meta sends for verification
    params = {
        "hub.mode": "subscribe",
        "hub.challenge": "test_challenge_12345",
        "hub.verify_token": "grace_webhook_token"
    }
    
    try:
        response = requests.get(base_url, params=params, timeout=10)
        
        print(f"📊 Webhook Verification Response:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Response Body: {response.text}")
        print(f"   Content-Type: {response.headers.get('content-type', 'N/A')}")
        
        if response.status_code == 200 and response.text == "test_challenge_12345":
            print("✅ Webhook verification endpoint working correctly!")
            return True
        else:
            print("❌ Webhook verification failed!")
            print(f"   Expected: 'test_challenge_12345'")
            print(f"   Got: '{response.text}'")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - webhook URL not accessible")
        print("   Make sure your app is deployed to fynko.space")
        return False
    except Exception as e:
        print(f"❌ Error testing webhook: {e}")
        return False

def test_local_webhook():
    """Test webhook locally if running on localhost."""
    
    print("\n🏠 Testing local webhook (if running locally)...")
    
    local_url = "http://127.0.0.1:8000/webhook"
    params = {
        "hub.mode": "subscribe", 
        "hub.challenge": "local_test_challenge",
        "hub.verify_token": "grace_webhook_token"
    }
    
    try:
        response = requests.get(local_url, params=params, timeout=5)
        
        print(f"📊 Local Webhook Response:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Local webhook working!")
        else:
            print("❌ Local webhook issue")
            
    except requests.exceptions.ConnectionError:
        print("⚠️  Local server not running (this is OK if deployed)")
    except Exception as e:
        print(f"❌ Local test error: {e}")

def check_webhook_requirements():
    """Check all webhook requirements."""
    
    print("\n📋 Checking Meta Webhook Requirements:")
    
    requirements = [
        {
            "name": "HTTPS URL",
            "requirement": "Webhook URL must use HTTPS",
            "status": "✅" if "https://" in "https://fynko.space/webhook" else "❌",
            "details": "fynko.space/webhook"
        },
        {
            "name": "Public accessibility", 
            "requirement": "URL must be publicly accessible",
            "status": "⚠️",
            "details": "Test by accessing https://fynko.space/webhook in browser"
        },
        {
            "name": "Verify token",
            "requirement": "Must return hub.challenge when verify token matches",
            "status": "⚠️",
            "details": "grace_webhook_token"
        },
        {
            "name": "Response format",
            "requirement": "Must return plain text challenge value",
            "status": "✅",
            "details": "PlainTextResponse implemented"
        }
    ]
    
    for req in requirements:
        print(f"   {req['status']} {req['name']}: {req['details']}")
    
    print(f"\n🔧 Meta Developer Console Configuration:")
    print(f"   Webhook URL: https://fynko.space/webhook")
    print(f"   Verify Token: grace_webhook_token")
    print(f"   Subscription Fields: messages")

def simulate_meta_verification():
    """Simulate what Meta does during webhook verification."""
    
    print(f"\n🤖 Simulating Meta's webhook verification process...")
    
    webhook_url = "https://fynko.space/webhook"
    verify_token = "grace_webhook_token"
    challenge = f"meta_challenge_{int(time.time())}"
    
    print(f"1. Meta sends GET request to: {webhook_url}")
    print(f"2. With parameters:")
    print(f"   - hub.mode=subscribe")
    print(f"   - hub.verify_token={verify_token}")
    print(f"   - hub.challenge={challenge}")
    
    params = {
        "hub.mode": "subscribe",
        "hub.verify_token": verify_token,
        "hub.challenge": challenge
    }
    
    try:
        print(f"\n📡 Making verification request...")
        response = requests.get(webhook_url, params=params, timeout=15)
        
        print(f"📊 Meta Verification Simulation:")
        print(f"   Status: {response.status_code}")
        print(f"   Response: '{response.text}'")
        print(f"   Expected: '{challenge}'")
        
        if response.status_code == 200 and response.text.strip() == challenge:
            print("✅ META VERIFICATION WOULD SUCCEED!")
            print("   Your webhook is properly configured")
        else:
            print("❌ META VERIFICATION WOULD FAIL!")
            print("   Check your webhook implementation")
            
    except Exception as e:
        print(f"❌ Verification simulation failed: {e}")

def show_debugging_steps():
    """Show debugging steps for webhook issues."""
    
    print(f"\n🔧 Webhook Debugging Steps:")
    print(f"\n1. Check if your app is deployed and running:")
    print(f"   Visit: https://fynko.space")
    print(f"   Should show: Instagram integration page")
    
    print(f"\n2. Test webhook endpoint manually:")
    print(f"   Visit: https://fynko.space/webhook?hub.mode=subscribe&hub.verify_token=grace_webhook_token&hub.challenge=test123")
    print(f"   Should return: test123")
    
    print(f"\n3. Check Meta Developer Console:")
    print(f"   Products → Webhooks → Instagram")
    print(f"   Callback URL: https://fynko.space/webhook")
    print(f"   Verify Token: grace_webhook_token")
    print(f"   Subscribe to: messages")
    
    print(f"\n4. Look for error messages in Meta Console")
    print(f"   Common issues:")
    print(f"   - URL not accessible (deployment issue)")
    print(f"   - Wrong verify token")
    print(f"   - Not returning plain text response")
    print(f"   - SSL certificate issues")
    
    print(f"\n5. Check webhook logs:")
    print(f"   Visit: https://fynko.space/webhook/logs")
    print(f"   Look for verification attempts")

if __name__ == "__main__":
    print("🚀 Meta Webhook Diagnostic Tool\n")
    
    # Test webhook verification
    webhook_works = test_webhook_verification()
    
    # Test local webhook if available
    test_local_webhook()
    
    # Check requirements
    check_webhook_requirements()
    
    # Simulate Meta's process
    if webhook_works:
        simulate_meta_verification()
    
    # Show debugging steps
    show_debugging_steps()
    
    print(f"\n🎯 Diagnostic complete!")
    print(f"   If webhook verification failed, follow the debugging steps above.")
    print(f"   If it succeeded, check Meta Developer Console for any error messages.")
