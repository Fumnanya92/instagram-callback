from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
import os
import httpx
from storage import save_token, load_token, clear_token
import json

router = APIRouter()


@router.get("/auth/callback")
async def auth_callback(request: Request):
    """Handle the Facebook Login redirect (manual flow).

    Steps:
    1. Exchange code -> short-lived token at Facebook Graph.
    2. Exchange short-lived -> long-lived token (fb_exchange_token).
    3. Persist long-lived token and redirect to `/`.
    """
    params = dict(request.query_params)
    print("Auth callback params:", params)

    code = params.get("code")
    if not code:
        return JSONResponse({"error": "missing_code", "params": params}, status_code=400)

    # Validate state for CSRF protection (optional but recommended)
    incoming_state = params.get("state")
    cookie_state = request.cookies.get("oauth_state")
    if cookie_state and incoming_state != cookie_state:
        return JSONResponse({"error": "invalid_state"}, status_code=400)

    client_id = os.getenv("FACEBOOK_APP_ID") or os.getenv("INSTAGRAM_CLIENT_ID")
    # Prefer the Facebook app secret if present; fall back to the Instagram client secret
    client_secret = os.getenv("FACEBOOK_APP_SECRET") or os.getenv("INSTAGRAM_CLIENT_SECRET")
    redirect_uri = os.getenv("INSTAGRAM_REDIRECT_URI")
    if not (client_id and client_secret and redirect_uri):
        return JSONResponse({"error": "oauth_not_configured"}, status_code=500)

    # 1) Exchange authorization code for a short-lived token
    short_lived_url = "https://graph.facebook.com/v23.0/oauth/access_token"
    params_exchange = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "client_secret": client_secret,
        "code": code,
    }

    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(short_lived_url, params=params_exchange)
    print(f"Short-lived exchange status: {r.status_code} body: {getattr(r, 'text', None)}")

    if r.status_code != 200:
        try:
            return JSONResponse(r.json(), status_code=r.status_code)
        except Exception:
            return JSONResponse({"error": "code_exchange_failed", "status_code": r.status_code}, status_code=500)

    body = r.json()
    short_lived = body.get("access_token")
    if not short_lived:
        return JSONResponse({"error": "no_access_token_in_response", "body": body}, status_code=500)

    # 2) Exchange the short-lived token for a long-lived token
    long_lived_url = "https://graph.facebook.com/v23.0/oauth/access_token"
    exchange_params = {
        "grant_type": "fb_exchange_token",
        "client_id": client_id,
        "client_secret": client_secret,
        "fb_exchange_token": short_lived,
    }

    async with httpx.AsyncClient(timeout=10) as client:
        r2 = await client.get(long_lived_url, params=exchange_params)
    print(f"Long-lived exchange status: {r2.status_code} body: {getattr(r2, 'text', None)}")

    if r2.status_code != 200:
        try:
            return JSONResponse(r2.json(), status_code=r2.status_code)
        except Exception:
            return JSONResponse({"error": "long_token_exchange_failed", "status_code": r2.status_code}, status_code=500)

    body2 = r2.json()
    long_lived = body2.get("access_token")
    if not long_lived:
        return JSONResponse({"error": "no_long_lived_token", "body": body2}, status_code=500)

    # persist token for reviewer/demo flow
    save_token(long_lived)

    # redirect reviewer back to the homepage where frontend will call /instagram/profile
    response = RedirectResponse(url="/")
    # clear the state cookie now that the flow is complete
    response.delete_cookie("oauth_state")
    return response


@router.get("/instagram/callback")
async def instagram_callback(request: Request):
    """Compatibility wrapper: some deployments use /instagram/callback as the
    redirect URI. Reuse the existing auth_callback implementation to avoid
    duplicating the exchange logic.
    """
    return await auth_callback(request)


@router.get("/delete-data")
async def delete_data():
    return {"message": "ok"}


@router.get("/deauthorize")
async def deauthorize():
    return {"message": "ok"}


@router.get("/instagram/profile")
def get_instagram_profile():
    # Load token from storage first, fall back to env var
    token = load_token() or os.getenv('INSTAGRAM_ACCESS_TOKEN')
    print(f"Loaded token present: {bool(token)}")
    if not token:
        raise HTTPException(status_code=401, detail="No access token configured")
    # Strategy:
    # 1) Call /me/accounts?fields=instagram_business_account to find any connected
    #    Instagram Business accounts via the user's Pages.
    # 2) If found, fetch the Instagram account by id with the desired fields.
    # 3) Fall back to a direct /me fields call as a last resort.

    pages_url = "https://graph.facebook.com/v23.0/me/accounts"
    params_pages = {"fields": "instagram_business_account", "access_token": token}
    r = httpx.get(pages_url, params=params_pages, timeout=10)
    if r.status_code != 200:
        # Return the upstream error to help debugging
        try:
            detail = r.json()
        except Exception:
            detail = {"error": "accounts_fetch_failed", "status_code": r.status_code}
        raise HTTPException(status_code=400, detail=detail)

    pages_body = r.json()
    for page in pages_body.get("data", []):
        ig = page.get("instagram_business_account")
        if ig and ig.get("id"):
            ig_id = ig["id"]
            profile_url = f"https://graph.facebook.com/v23.0/{ig_id}"
            # account_type is not available on IGUser nodes in some API versions;
            # avoid requesting it to prevent (#100) errors. Request the common
            # fields that are usually present on IGUser nodes.
            params_profile = {"fields": "id,username,profile_picture_url", "access_token": token}
            r2 = httpx.get(profile_url, params=params_profile, timeout=10)
            print(f"Profile fetch {profile_url} status: {r2.status_code} body: {r2.text}")
            if r2.status_code != 200:
                try:
                    return JSONResponse(r2.json(), status_code=r2.status_code)
                except Exception:
                    raise HTTPException(status_code=400, detail={"error": "instagram_profile_fetch_failed", "status_code": r2.status_code})
            return JSONResponse(r2.json())

    # Fallback: try direct /me fields (may work for non-business IG tokens)
    fallback_url = "https://graph.facebook.com/v23.0/me"
    params_fallback = {"fields": "id,username,profile_picture_url", "access_token": token}
    r3 = httpx.get(fallback_url, params=params_fallback, timeout=10)
    print(f"Fallback /me fetch status: {r3.status_code} body: {r3.text}")
    if r3.status_code == 200:
        return JSONResponse(r3.json())

    # No IG account found; return helpful debug info
    raise HTTPException(status_code=400, detail={
        "error": "no_instagram_business_account_found",
        "pages": pages_body.get("data", []),
    })


@router.get("/token")
def view_token():
    """Return whether a token is stored (for testing only)."""
    token = load_token()
    return {"stored": bool(token)}


@router.delete("/token")
def delete_token():
    """Clear stored token (testing/admin)."""
    clear_token()
    return {"cleared": True}


@router.get("/token/content")
def token_content(raw: bool = False):
    """Return the stored token in masked form.

    By default this returns a masked token to avoid accidental leakage.
    To retrieve the raw token set the environment variable `ALLOW_TOKEN_INSPECT=1`
    and call with `?raw=1` (only for local debugging).
    """
    token = load_token()
    if not token:
        return JSONResponse({"token_present": False}, status_code=404)

    def mask(s: str) -> str:
        if not s:
            return ""
        if len(s) <= 8:
            return "****"
        return f"{s[:4]}...{s[-4:]}"

    allow_raw = os.getenv("ALLOW_TOKEN_INSPECT") == "1"
    if raw and not allow_raw:
        return JSONResponse({"error": "raw_inspect_not_allowed", "note": "set ALLOW_TOKEN_INSPECT=1 to enable raw token output"}, status_code=403)

    return JSONResponse({"token_present": True, "token": token if (raw and allow_raw) else mask(token)})


@router.get("/debug/oauth")
def debug_oauth():
    """Return masked OAuth env values and simple validity checks (safe for logs).

    This endpoint intentionally masks sensitive values. Use this to confirm
    that the deployed process sees the expected env vars.
    """
    def mask(s: str):
        if not s:
            return None
        s = str(s)
        if len(s) <= 6:
            return "***"
        return s[:3] + "..." + s[-3:]

    fb_app = os.getenv("FACEBOOK_APP_ID") or os.getenv("INSTAGRAM_CLIENT_ID")
    redirect = os.getenv("INSTAGRAM_REDIRECT_URI")

    fb_secret = os.getenv("FACEBOOK_APP_SECRET")
    ig_secret = os.getenv("INSTAGRAM_CLIENT_SECRET")
    secret_used = None
    if fb_secret:
        secret_used = "FACEBOOK_APP_SECRET"
    elif ig_secret:
        secret_used = "INSTAGRAM_CLIENT_SECRET"

    return {
        "facebook_app_id_masked": mask(fb_app),
        "facebook_app_id_present": bool(fb_app),
        "secret_used": secret_used,
        "client_secret_present": bool(fb_secret or ig_secret),
        "redirect_uri": redirect,
    }


@router.get("/token/inspect")
def inspect_token():
    """Inspect the stored access token using Facebook's debug_token endpoint.

    Returns the debug_token payload. Requires INSTAGRAM_CLIENT_SECRET to be set
    so we can build an app access token (app_id|app_secret).
    """
    token = load_token() or os.getenv('INSTAGRAM_ACCESS_TOKEN')
    if not token:
        return JSONResponse({"error": "no_token"}, status_code=400)

    app_id = os.getenv("FACEBOOK_APP_ID") or os.getenv("INSTAGRAM_CLIENT_ID")
    app_secret = os.getenv("FACEBOOK_APP_SECRET") or os.getenv("INSTAGRAM_CLIENT_SECRET")
    if not (app_id and app_secret):
        return JSONResponse({"error": "app_credentials_missing"}, status_code=500)

    app_access = f"{app_id}|{app_secret}"
    url = "https://graph.facebook.com/debug_token"
    params = {"input_token": token, "access_token": app_access}
    r = httpx.get(url, params=params, timeout=10)
    try:
        return JSONResponse(r.json(), status_code=r.status_code)
    except Exception:
        return JSONResponse({"error": "debug_failed"}, status_code=500)
