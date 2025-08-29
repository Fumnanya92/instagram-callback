from fastapi import FastAPI, Request

app = FastAPI()


@app.get("/")
async def root():
    """Simple health check for Render and Uptime monitors."""
    return {"message": "Instagram Callback Service is running 🚀"}


@app.get("/callback")
async def callback(code: str = None, error: str = None):
    """A tiny convenience endpoint for manual testing.

    Note: keep `/instagram/callback` for the real OAuth redirect.
    """
    if error:
        return {"error": error}
    return {"code": code}


@app.get("/instagram/callback")
async def instagram_callback(request: Request):
    params = dict(request.query_params)
    # log to stdout so Render will capture it
    print("Instagram callback params:", params)
    return {"status": "success", "params": params}


@app.get("/auth/callback")
async def auth_callback(request: Request):
    """Compatibility route for deployments that use /auth/callback.

    Mirrors the behaviour of `/instagram/callback` and logs the query params.
    """
    params = dict(request.query_params)
    print("Auth callback params:", params)
    return {"status": "success", "params": params}


@app.get("/delete-data")
async def delete_data():
    """Endpoint required by Meta for data deletion verification."""
    return {"message": "ok"}


@app.get("/deauthorize")
async def deauthorize():
    """Endpoint required by Meta for deauthorization callbacks."""
    return {"message": "ok"}
