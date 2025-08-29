from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
import os
import requests
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
            r = requests.post(token_url, data=data, timeout=10)
            if r.status_code == 200:
                body = r.json()
                token = body.get("access_token") or body.get("access_token")
                if token:
                    save_token(token)
                    return {"status": "success", "stored": True}
            return JSONResponse(r.json(), status_code=r.status_code)

    return {"status": "success", "params": params}


@router.get("/auth/callback")
async def auth_callback(request: Request):
    params = dict(request.query_params)
    print("Auth callback params:", params)
    return {"status": "success", "params": params}


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
    r = requests.get(url, params=params, timeout=10)
    if r.status_code != 200:
        raise HTTPException(status_code=400, detail=r.json())
    return JSONResponse(r.json())
