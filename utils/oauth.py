from typing import Optional
import os
import urllib.parse


def build_auth_url(
    client_id: Optional[str] = None,
    redirect_uri: Optional[str] = None,
    scope: Optional[str] = None,
    api_version: str = "v23.0",
    state: Optional[str] = None,
) -> str:
    """Return a Facebook OAuth dialog URL using provided values or environment.

    This centralizes the auth URL generation to avoid duplication between
    routes and makes it easy to tweak the endpoint/version in one place.
    """
    # For Instagram Business / Graph flows we must use the Facebook App ID
    client_id = client_id or os.getenv("FACEBOOK_APP_ID")
    redirect_uri = redirect_uri or os.getenv("INSTAGRAM_REDIRECT_URI")
    # Use the Instagram Graph / Facebook Login permissions. The old
    # 'instagram_business_*' names are invalid in the Login dialog.
    # Common permissions needed for Instagram Business + messaging:
    # - instagram_basic
    # - instagram_manage_messages
    # - pages_show_list (to list pages connected to the user)
    scope = scope or os.getenv("INSTAGRAM_OAUTH_SCOPE", "instagram_basic,instagram_manage_messages,pages_show_list")

    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": scope,
        "response_type": "code",
    }
    if state:
        params["state"] = state

    return f"https://www.facebook.com/{api_version}/dialog/oauth?" + urllib.parse.urlencode(params)


def mask_client_id(client_id: Optional[str]) -> Optional[str]:
    if not client_id:
        return None
    s = str(client_id)
    if len(s) <= 6:
        return "***"
    return s[:3] + "..." + s[-3:]


def generate_state(length: int = 24) -> str:
    """Generate a secure random state string for CSRF protection."""
    import secrets

    return secrets.token_urlsafe(length)
