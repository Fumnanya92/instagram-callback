from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
import os
import httpx
from storage import save_token, load_token, clear_token

router = APIRouter()


@router.get("/callback")
async def callback(code: str = None, error: str = None):
    if error:
        return {"error": error}
    return {"code": code}


@router.get("/instagram/callback")
async def instagram_callback(request: Request):
    params = dict(request.query_params)
    print("Instagram callback params:", params)

    # If access_token returned directly, save it for reviewer flow
    access_token = params.get("access_token")
    if access_token:
        save_token(access_token)
        return {"status": "success", "stored": True}

    # If 'code' returned, we may exchange it for a token if client creds are set
    code = params.get("code")
    if code:
        client_id = os.getenv("INSTAGRAM_CLIENT_ID")
        client_secret = os.getenv("INSTAGRAM_CLIENT_SECRET")
        redirect_uri = os.getenv("INSTAGRAM_REDIRECT_URI")
        if client_id and client_secret and redirect_uri:
            # Exchange code for access token (Instagram Basic Display flow)
            token_url = "https://api.instagram.com/oauth/access_token"
            data = {
                "client_id": client_id,
                "client_secret": client_secret,
                "grant_type": "authorization_code",
                "redirect_uri": redirect_uri,
                "code": code,
            }
            async with httpx.AsyncClient(timeout=10) as client:
                r = await client.post(token_url, data=data)
            if r.status_code == 200:
                body = r.json()
                token = body.get("access_token")
                if token:
                    save_token(token)
                    return {"status": "success", "stored": True}
            try:
                return JSONResponse(r.json(), status_code=r.status_code)
            except Exception:
                return JSONResponse({"error": "token_exchange_failed"}, status_code=500)

    return {"status": "success", "params": params}


@router.get("/auth/callback")
async def auth_callback(request: Request):
    """Handle Instagram OAuth redirect with ?code=.

    Exchanges the code for a short-lived token, exchanges that for a long-lived
    token, saves the long-lived token via save_token(), then redirects to `/`.
    """
    params = dict(request.query_params)
    print("Auth callback params:", params)

    code = params.get("code")
    if not code:
        return JSONResponse({"error": "missing_code", "params": params}, status_code=400)

    client_id = os.getenv("INSTAGRAM_CLIENT_ID")
    client_secret = os.getenv("INSTAGRAM_CLIENT_SECRET")
    redirect_uri = os.getenv("INSTAGRAM_REDIRECT_URI")
    if not (client_id and client_secret and redirect_uri):
        return JSONResponse({"error": "oauth_not_configured"}, status_code=500)

    # Exchange code for short-lived token
    token_url = "https://api.instagram.com/oauth/access_token"
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri,
        "code": code,
    }

    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.post(token_url, data=data)

    if r.status_code != 200:
        # propagate Instagram's error to the caller (useful during review)
        try:
            return JSONResponse(r.json(), status_code=r.status_code)
        except Exception:
            return JSONResponse({"error": "token_exchange_failed", "status_code": r.status_code}, status_code=500)

    body = r.json()
    short_lived = body.get("access_token")
    if not short_lived:
        return JSONResponse({"error": "no_access_token_in_response", "body": body}, status_code=500)

    # Exchange short-lived token for long-lived token
    exchange_url = "https://graph.instagram.com/access_token"
    params2 = {
        "grant_type": "ig_exchange_token",
        "client_secret": client_secret,
        "access_token": short_lived,
    }

    async with httpx.AsyncClient(timeout=10) as client:
        r2 = await client.get(exchange_url, params=params2)

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
    return RedirectResponse(url="/")


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
    url = "https://graph.instagram.com/me"
    params = {
        "fields": "id,username,account_type,profile_picture_url",
        "access_token": token,
    }
    # Use httpx (imported above) instead of requests to keep async/http clients consistent
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


@router.get("/debug/oauth")
def debug_oauth():
    """Return masked OAuth env values and simple validity checks for debugging."""
    client_id = os.getenv("INSTAGRAM_CLIENT_ID")
    redirect_uri = os.getenv("INSTAGRAM_REDIRECT_URI")
    scope = os.getenv("INSTAGRAM_OAUTH_SCOPE")

    def mask(s: str) -> str:
        if not s:
            return ""
        if len(s) <= 8:
            return s[0] + "*" * (len(s) - 2) + s[-1]
        return s[:4] + "*" * (len(s) - 8) + s[-4:]

    info = {
        "client_id_provided": bool(client_id),
        "client_id_masked": mask(client_id) if client_id else None,
        "client_id_length": len(client_id) if client_id else 0,
        "client_id_numeric": client_id.isdigit() if client_id else False,
        "redirect_uri": redirect_uri,
        "scope": scope,
    }
    return JSONResponse(info)


@router.get("/debug/oauth")
def debug_oauth():
    """Return masked OAuth env values and simple validity checks to help debug Invalid App ID errors.

    Note: This intentionally masks most of the client_id to avoid exposing secrets in logs.
    """
    client_id = os.getenv("INSTAGRAM_CLIENT_ID") or os.getenv("FACEBOOK_APP_ID")
    redirect_uri = os.getenv("INSTAGRAM_REDIRECT_URI")

    def mask(s: str):
        if not s:
            return None
        if len(s) <= 6:
            return "***"
        return s[:3] + "..." + s[-3:]

    client_id_masked = mask(client_id) if client_id else None
    client_id_valid = False
    if client_id and client_id.isdigit() and len(client_id) >= 5:
        client_id_valid = True

    redirect_uri_valid = False
    if redirect_uri and (redirect_uri.startswith("https://") or redirect_uri.startswith("http://")):
        redirect_uri_valid = True

    return {
        "client_id_masked": client_id_masked,
        "client_id_present": bool(client_id),
        "client_id_valid_format": client_id_valid,
        "redirect_uri": redirect_uri,
        "redirect_uri_valid_format": redirect_uri_valid,
        "note": "If client_id_present is true but client_id_valid_format is false, the app id may be malformed. Ensure the Facebook App ID (numeric) is set in INSTAGRAM_CLIENT_ID on Render."
    }
