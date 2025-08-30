from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import os

from utils.oauth import build_auth_url, generate_state

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
    if not client_id or not redirect_uri:
        # show a small page telling the reviewer that login isn't configured
        return HTMLResponse(f"<html><body><h3>Login not configured</h3><p>Set INSTAGRAM_CLIENT_ID and INSTAGRAM_REDIRECT_URI in environment.</p></body></html>")

    # Build the OAuth URL (centralized helper). The helper reads
    # `INSTAGRAM_OAUTH_SCOPE` from environment and provides a safe
    # default; avoid duplicating scope defaults here to prevent
    # conflicting/invalid permission names.
    # generate CSRF state and store it in a secure cookie
    state = generate_state()
    auth_url = build_auth_url(state=state)
    print(f"Generated auth_url: {auth_url}")
    response = RedirectResponse(auth_url)
    # set cookie for later validation in /auth/callback; secure flag depends on deployment
    response.set_cookie("oauth_state", state, httponly=True, secure=True, samesite="lax")
    return response
