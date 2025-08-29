from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

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
