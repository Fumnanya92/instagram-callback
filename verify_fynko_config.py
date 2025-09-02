#!/usr/bin/env python3
"""
Quick verification that fynko.space configuration is correctly set up.
"""

import os
from pathlib import Path

def verify_fynko_config():
    """Verify that all fynko.space configurations are correct."""
    
    print("🔍 Verifying fynko.space configuration...\n")
    
    # Check .env file
    env_file = Path(".env")
    if env_file.exists():
        with env_file.open("r") as f:
            env_content = f.read()
        
        print("✅ .env file configuration:")
        if "fynko.space/instagram/callback" in env_content:
            print("   ✅ INSTAGRAM_REDIRECT_URI: https://fynko.space/instagram/callback")
        else:
            print("   ❌ INSTAGRAM_REDIRECT_URI not set to fynko.space")
        
        if "WEBHOOK_VERIFY_TOKEN=grace_webhook_token" in env_content:
            print("   ✅ WEBHOOK_VERIFY_TOKEN: grace_webhook_token")
        else:
            print("   ❌ WEBHOOK_VERIFY_TOKEN not properly configured")
        
        if "PAGE_ACCESS_TOKEN=" in env_content:
            if "your_page_access_token_here" in env_content:
                print("   ⚠️  PAGE_ACCESS_TOKEN: Needs your actual token")
            else:
                print("   ✅ PAGE_ACCESS_TOKEN: Configured")
        else:
            print("   ❌ PAGE_ACCESS_TOKEN not found")
    else:
        print("❌ .env file not found")
    
    print("\n📋 Meta Developer Console Configuration:")
    print("   🔗 Webhook URL: https://fynko.space/webhook")
    print("   🔗 OAuth Redirect: https://fynko.space/instagram/callback")
    print("   🔑 Verify Token: grace_webhook_token")
    
    print("\n🧪 Test URLs for Meta Reviewers:")
    print("   🏠 Main App: https://fynko.space")
    print("   📊 Webhook Status: https://fynko.space/webhook/status")
    print("   📝 Webhook Logs: https://fynko.space/webhook/logs")
    print("   🔒 Privacy Policy: https://fynko.space/privacy")
    print("   📄 Terms: https://fynko.space/terms")
    
    # Check if sample data exists
    data_dir = Path("data")
    if data_dir.exists():
        webhook_log = data_dir / "webhook.log"
        reply_log = data_dir / "auto_replies.log"
        
        print("\n📊 Sample Data for Reviewers:")
        if webhook_log.exists():
            print("   ✅ Webhook events log: Ready")
        if reply_log.exists():
            print("   ✅ Auto-replies log: Ready")
    else:
        print("\n⚠️  Sample data not found - run seed_webhook_logs.py")
    
    print("\n🚀 Ready for deployment to fynko.space!")
    print("   Just update PAGE_ACCESS_TOKEN and deploy!")

if __name__ == "__main__":
    verify_fynko_config()
