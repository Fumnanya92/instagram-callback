from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import os
import urllib.parse

router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    # The frontend will call /instagram/profile to populate reviewer info
    return templates.TemplateResponse("welcome.html", {"request": request})


@router.get("/privacy", response_class=HTMLResponse)
async def privacy(request: Request):
    return templates.TemplateResponse("privacy.html", {"request": request})


@router.get("/terms", response_class=HTMLResponse)
async def terms(request: Request):
    return templates.TemplateResponse("terms.html", {"request": request})



@router.get("/login")
async def login_redirect(request: Request):
    """Start Instagram OAuth by redirecting the reviewer to the authorize URL.

    Requires INSTAGRAM_CLIENT_ID and INSTAGRAM_REDIRECT_URI env vars to be set in Render.
    """
    client_id = os.getenv("INSTAGRAM_CLIENT_ID")
    redirect_uri = os.getenv("INSTAGRAM_REDIRECT_URI")
    scope = os.getenv("INSTAGRAM_OAUTH_SCOPE", "user_profile")
    if not client_id or not redirect_uri:
        # show a small page telling the reviewer that login isn't configured
        return HTMLResponse(f"<html><body><h3>Login not configured</h3><p>Set INSTAGRAM_CLIENT_ID and INSTAGRAM_REDIRECT_URI in environment.</p></body></html>")

    # Build the OAuth URL using Facebook's dialog (Instagram Graph requires Facebook Login)
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": scope,
        "response_type": "code",
    }
    auth_url = "https://www.facebook.com/v19.0/dialog/oauth?" + urllib.parse.urlencode(params)
    # Log the full auth URL so we can inspect exact redirect_uri being sent
    print(f"Generated auth_url: {auth_url}")
    return RedirectResponse(auth_url)
