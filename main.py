from fastapi import FastAPI
import os

# If a local .env file exists, load it for local development so the app uses
# the same environment variables you'd set on Render. This is safe because
# `.env` is in `.gitignore` and won't be committed.
if os.path.exists('.env'):
	try:
		from dotenv import load_dotenv

		load_dotenv('.env')
	except Exception:
		# python-dotenv isn't installed locally; that's okay for production
		pass

from routes.web import router as web_router
from routes.api import router as api_router
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse


app = FastAPI()

# include routers
app.include_router(api_router)
app.include_router(web_router)

# Serve static assets from /static
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/flutter/privacy.html")
async def flutter_privacy():
    return FileResponse("static/flutter/privacy.html")

@app.get("/AccesscodeNG/privacy.html")
async def flutter_privacy():
    return FileResponse("static/AccesscodeNG/privacy.html")