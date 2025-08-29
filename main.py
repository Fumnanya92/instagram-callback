from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
import os
import requests

app = FastAPI()


@app.get("/")
async def root():
        """Welcome page for reviewers and users. Fetches profile via JS after auth."""
        return HTMLResponse("""
        <!doctype html>
        <html>
            <head>
                <meta charset="utf-8" />
                <meta name="viewport" content="width=device-width,initial-scale=1" />
                <title>Grace — Instagram Callback</title>
                <style>
                    :root{--bg:#0f172a;--card:#0b1220;--accent:#7c3aed;--muted:#94a3b8}
                    body{margin:0;font-family:Inter,system-ui,Segoe UI,Roboto,Helvetica,Arial,sans-serif;background:linear-gradient(180deg,#071027 0%, #071733 100%);color:#e6eef8;min-height:100vh;display:flex;align-items:center;justify-content:center}
                    .card{width:980px;max-width:95%;background:linear-gradient(180deg,rgba(255,255,255,0.02),rgba(255,255,255,0.01));border-radius:14px;padding:28px;box-shadow:0 10px 30px rgba(2,6,23,0.6);display:flex;gap:24px;align-items:center}
                    .brand{flex:1}
                    .brand h1{margin:0;font-size:28px;letter-spacing: -0.02em}
                    .brand p{color:var(--muted);margin-top:8px}
                    .actions{display:flex;flex-direction:column;gap:12px;align-items:flex-end}
                    .btn{background:var(--accent);color:white;padding:10px 16px;border-radius:10px;border:none;cursor:pointer;font-weight:600}
                    .profile{display:flex;gap:16px;align-items:center}
                    .avatar{width:72px;height:72px;border-radius:999px;background:#fff;overflow:hidden;flex-shrink:0}
                    .meta p{margin:0}
                    .muted{color:var(--muted)}
                </style>
            </head>
            <body>
                <div class="card">
                    <div class="brand">
                        <h1>Grace — AI Virtual Business Assistant</h1>
                        <p class="muted">Minimal reviewer UI — shows Instagram username, profile picture and account id after login.</p>
                        <div style="margin-top:16px;display:flex;gap:12px;align-items:center">
                            <button class="btn" onclick="location.href='/login'">Start Login</button>
                            <a class="muted" href="/privacy" style="text-decoration:none;color:inherit">Privacy</a>
                            <a class="muted" href="/terms" style="text-decoration:none;color:inherit;margin-left:8px">Terms</a>
                        </div>
                    </div>

                    <div class="actions">
                        <div id="profileBox" style="min-width:260px;display:none" class="profile card-right">
                            <div class="avatar"><img id="avatar" src="" alt="avatar" style="width:100%;height:100%;object-fit:cover"/></div>
                            <div class="meta">
                                <p id="username"><strong>Username</strong></p>
                                <p id="acctid" class="muted">ID</p>
                                <p id="type" class="muted">Type</p>
                            </div>
                        </div>
                        <div id="status" class="muted">Not logged in</div>
                    </div>
                </div>

                <script>
                    async function fetchProfile(){
                        try{
                            const res = await fetch('/instagram/profile');
                            if(!res.ok) throw new Error('no-profile');
                            const data = await res.json();
                            document.getElementById('avatar').src = data.profile_picture_url || '';
                            document.getElementById('username').innerHTML = '<strong>@'+(data.username||'')+'</strong>';
                            document.getElementById('acctid').textContent = 'ID: ' + (data.id||'');
                            document.getElementById('type').textContent = 'Type: ' + (data.account_type||'');
                            document.getElementById('profileBox').style.display = 'flex';
                            document.getElementById('status').textContent = 'Logged in — profile loaded';
                        }catch(e){
                            document.getElementById('status').textContent = 'No active session — please complete Instagram login in your app.';
                        }
                    }
                    // try to fetch on load
                    fetchProfile();
                </script>
            </body>
        </html>
        """)


@app.get("/health")
async def health():
        return JSONResponse({"status": "ok", "service": "instagram-callback"})


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


@app.get("/privacy", response_class=None)
async def privacy():
        """Serve a simple privacy policy page as HTML for App Review."""
        return HTMLResponse("""
        <html>
            <head><title>Privacy Policy</title></head>
            <body style="font-family: Arial, sans-serif; margin: 40px;">
                <h1>Privacy Policy</h1>
                <p><strong>Last updated:</strong> August 2025</p>
                <p>Grace ("the App") is a messaging assistant that helps users interact with businesses and services through platforms like Instagram and WhatsApp.</p>

                <h2>Information We Collect</h2>
                <ul>
                    <li>Basic profile details (such as name, email, or username) if provided.</li>
                    <li>Messages and interactions necessary for responding to your requests.</li>
                    <li>Technical information such as timestamps for service operation.</li>
                </ul>

                <h2>How We Use Information</h2>
                <ul>
                    <li>To deliver automated replies and services requested by you.</li>
                    <li>To improve the functionality and reliability of the App.</li>
                    <li>To ensure compliance with platform policies.</li>
                </ul>

                <h2>Data Sharing</h2>
                <p>We do <strong>not</strong> sell, rent, or trade your data. Data may only be shared if required by law or to comply with platform requirements.</p>

                <h2>Data Retention & Deletion</h2>
                <p>Data is stored only as long as needed to provide the service.</p>
                <p>You may request deletion of your data at any time by visiting: <a href="https://fynko.space/delete-data">https://fynko.space/delete-data</a></p>

                <h2>Contact</h2>
                <p>Email: fumnanya541@gmail.com</p>
            </body>
        </html>
        """)


@app.get("/terms", response_class=None)
async def terms():
        """Serve a simple Terms of Service page as HTML for App Review."""
        return HTMLResponse("""
        <html>
            <head><title>Terms of Service</title></head>
            <body style="font-family: Arial, sans-serif; margin: 40px;">
                <h1>Terms of Service</h1>
                <p><strong>Last updated:</strong> August 2025</p>

                <h2>1. Use of Service</h2>
                <p>Grace is provided to assist with automated messaging and related services. You agree to use the App only in compliance with applicable laws and platform policies.</p>

                <h2>2. User Responsibilities</h2>
                <ul>
                    <li>Do not use the App for unlawful, harmful, or abusive purposes.</li>
                    <li>You are responsible for the accuracy of information you provide.</li>
                </ul>

                <h2>3. Data Handling</h2>
                <p>By using the App, you consent to the collection and use of data as described in the Privacy Policy.</p>
                <p>You may request data deletion at: <a href="https://fynko.space/delete-data">https://fynko.space/delete-data</a></p>

                <h2>4. Disclaimer</h2>
                <p>The App is provided “as is” without warranties of any kind. We are not responsible for any damages arising from the use of the App.</p>

                <h2>5. Changes to Terms</h2>
                <p>We may update these Terms from time to time. Continued use of the App means you accept the updated Terms.</p>

                <h2>Contact</h2>
                <p>Email: fumnanya541@gmail.com</p>
            </body>
        </html>
        """)
