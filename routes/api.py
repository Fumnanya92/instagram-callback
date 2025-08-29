from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
import os
import httpx
from storage import save_token, load_token, clear_token

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
    client_secret = os.getenv("INSTAGRAM_CLIENT_SECRET")
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
    if not token:
        raise HTTPException(status_code=401, detail="No access token configured")

    # Use Facebook Graph to fetch the connected Instagram Business account info
    url = "https://graph.facebook.com/v23.0/me"
    params = {
        "fields": "id,username,account_type,profile_picture_url",
        "access_token": token,
    }

    r = httpx.get(url, params=params, timeout=10)
    if r.status_code != 200:
        raise HTTPException(status_code=400, detail=r.json())
    return JSONResponse(r.json())


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
