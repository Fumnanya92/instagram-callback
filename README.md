# Instagram Callback (FastAPI)

This tiny FastAPI app exposes a callback endpoint for the Instagram OAuth flow.

Files:
- `main.py` — FastAPI app with `/instagram/callback` GET endpoint.
- `requirements.txt` — minimal dependencies.

Quick start (locally):

1. Create and activate a virtual environment.
2. Install dependencies:

   pip install -r requirements.txt

3. Run locally:

   uvicorn main:app --reload --host 127.0.0.1 --port 8000

Render deployment notes:

- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn main:app --host 0.0.0.0 --port 10000`
- Add custom domain `fynko.space` and set the OAuth redirect in Meta to `https://fynko.space/instagram/callback`.

Once pushed to GitHub you can connect the repo in Render and deploy the service.
