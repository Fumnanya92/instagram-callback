#!/usr/bin/env python3
"""
Test Graph API calls for Instagram Business account integration.
"""

import requests
import json
import sys

def test_page_instagram_account():
    """Test getting Instagram Business account from a Facebook Page."""
    
    # Your page ID and access token from the command
    page_id = "189410577578969"
    access_token = "EAAUwvOmbLXEBPbp32FZBYJQLbCOk03TobTzZBjIabI5nW6loYqEC8yEZC1I9fDzNJikPZB0yVrAOXn8Fs8QgdmEQsBYg1HMngaWFI4WHjfM643iK3loOe8pZCWOvgLCexGxINENfa1q2tWqy84o3RRZCGAhUEEElbDt3ul0xZASu5nC274lpsNX3bVpcMNZAIg6jpVrmAchKrlzFullKQhR7uTnZBFcho8ViPTiOCiE6lDmtsbVyM"
    
    # Graph API endpoint
    url = f"https://graph.facebook.com/v20.0/{page_id}"
    params = {
        "fields": "instagram_business_account",
        "access_token": access_token
    }
    
    print(f"🔍 Testing Graph API call...")
    print(f"📍 Endpoint: {url}")
    print(f"📋 Fields: {params['fields']}")
    print(f"🔑 Token: {access_token[:20]}...")
    print()
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📄 Response Headers:")
        for key, value in response.headers.items():
            if key.lower() in ['content-type', 'x-fb-trace-id', 'x-fb-rev']:
                print(f"   {key}: {value}")
        print()
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Success! Response:")
            print(json.dumps(data, indent=2))
            
            # Check if Instagram Business account is linked
            ig_account = data.get("instagram_business_account")
            if ig_account:
                print(f"\n✅ Instagram Business Account Found:")
                print(f"   ID: {ig_account.get('id')}")
                
                # Test getting Instagram account details
                test_instagram_profile(ig_account.get('id'), access_token)
            else:
                print("\n⚠️  No Instagram Business account linked to this page")
                
        else:
            print("❌ Error Response:")
            try:
                error_data = response.json()
                print(json.dumps(error_data, indent=2))
            except:
                print(response.text)
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network Error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_instagram_profile(ig_account_id, access_token):
    """Test getting Instagram profile details."""
    
    if not ig_account_id:
        return
        
    print(f"\n🔍 Testing Instagram profile fetch...")
    
    url = f"https://graph.facebook.com/v20.0/{ig_account_id}"
    params = {
        "fields": "id,username,profile_picture_url,followers_count,media_count",
        "access_token": access_token
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        print(f"📊 Instagram Profile Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Instagram Profile:")
            print(json.dumps(data, indent=2))
        else:
            print("❌ Instagram Profile Error:")
            try:
                error_data = response.json()
                print(json.dumps(error_data, indent=2))
            except:
                print(response.text)
                
    except Exception as e:
        print(f"❌ Instagram Profile Error: {e}")

def test_token_validity():
    """Test if the access token is valid."""
    
    access_token = "EAAUwvOmbLXEBPbp32FZBYJQLbCOk03TobTzZBjIabI5nW6loYqEC8yEZC1I9fDzNJikPZB0yVrAOXn8Fs8QgdmEQsBYg1HMngaWFI4WHjfM643iK3loOe8pZCWOvgLCexGxINENfa1q2tWqy84o3RRZCGAhUEEElbDt3ul0xZASu5nC274lpsNX3bVpcMNZAIg6jpVrmAchKrlzFullKQhR7uTnZBFcho8ViPTiOCiE6lDmtsbVyM"
    
    print(f"🔍 Testing token validity...")
    
    url = "https://graph.facebook.com/v20.0/me"
    params = {"access_token": access_token}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        print(f"📊 Token Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Token Valid - User/Page Info:")
            print(json.dumps(data, indent=2))
        else:
            print("❌ Token Error:")
            try:
                error_data = response.json()
                print(json.dumps(error_data, indent=2))
            except:
                print(response.text)
                
    except Exception as e:
        print(f"❌ Token Test Error: {e}")

if __name__ == "__main__":
    print("🧪 Testing Graph API Integration\n")
    
    # Test token validity first
    test_token_validity()
    print("\n" + "="*50 + "\n")
    
    # Test page Instagram account
    test_page_instagram_account()
    
    print(f"\n🎯 Test complete!")
