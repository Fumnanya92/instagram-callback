# Meta Developer Console Webhook Setup Guide

## 📱 Complete Meta Webhook Configuration

### Step 1: Access Meta Developer Console
1. Go to: https://developers.facebook.com/apps
2. Select your app: **Grace Instagram Integration**
3. Navigate to **App Dashboard**

### Step 2: Add Webhooks Product
1. Click **"Add Product"** in left sidebar
2. Find **"Webhooks"** and click **"Set Up"**
3. If already added, click **"Webhooks"** in left sidebar

### Step 3: Configure Instagram Webhooks
1. In Webhooks page, look for **"Instagram"** section
2. Click **"Edit"** or **"Add Subscription"** for Instagram
3. Enter webhook details:
   ```
   Callback URL: https://fynko.space/webhook
   Verify Token: grace_webhook_token
   ```
4. Click **"Verify and Save"**

### Step 4: Subscribe to Events
After verification succeeds:
1. Check **"messages"** in the subscription fields
2. Click **"Save"** or **"Subscribe"**

### Step 5: Verify Success
You should see:
- ✅ Green checkmark next to Instagram webhooks
- ✅ "messages" listed under subscribed fields
- ✅ Status showing "Active" or "Subscribed"

## 🔧 Troubleshooting Common Issues

### Issue 1: "URL not reachable"
**Solution**: 
- Ensure https://fynko.space is deployed and running
- Test URL manually: https://fynko.space/webhook?hub.mode=subscribe&hub.verify_token=grace_webhook_token&hub.challenge=test123
- Should return: test123

### Issue 2: "Verification failed" 
**Solution**:
- Double-check verify token: `grace_webhook_token` (exact match)
- Ensure no extra spaces or characters
- Token is case-sensitive

### Issue 3: "SSL certificate error"
**Solution**:
- Ensure fynko.space has valid SSL certificate
- Test HTTPS access in browser

### Issue 4: No confirmation message
**Possible causes**:
1. **Silent success**: Some apps don't show confirmation - check if webhook appears in list
2. **Permission issue**: Ensure you have admin access to the Facebook app
3. **Cache issue**: Refresh the page and try again

### Issue 5: Meta Console showing old URL
**Solution**:
- Clear browser cache
- Try incognito/private browsing mode
- Wait a few minutes and retry

## 🎯 Expected Behavior

### During Setup:
1. Enter webhook URL and verify token
2. Meta sends GET request to verify
3. Your app returns the challenge
4. Meta shows success message or green indicator
5. Webhook appears in subscriptions list

### After Setup:
- Instagram webhook listed as "Active"
- "messages" subscription enabled
- Ready to receive DM events

## 📊 Testing Your Setup

### Test 1: Manual Verification
Visit this URL in browser:
```
https://fynko.space/webhook?hub.mode=subscribe&hub.verify_token=grace_webhook_token&hub.challenge=manual_test
```
Should return: `manual_test`

### Test 2: Check Webhook Status
Visit: https://fynko.space/webhook/status
Should show webhook configuration details

### Test 3: Send Test Message
1. Send DM to @thepixiehive Instagram account
2. Check logs: https://fynko.space/webhook/logs
3. Should see incoming message and auto-reply

## 🚨 If Still Having Issues

1. **Screenshot the error** in Meta Developer Console
2. **Check exact error message** displayed
3. **Verify app permissions** - you need admin access
4. **Try different browser** or incognito mode
5. **Contact Meta support** if webhook verification keeps failing

Your webhook URL is confirmed working, so the issue is likely in the Meta Console UI or permissions.
