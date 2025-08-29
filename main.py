from fastapi import FastAPI, Request

app = FastAPI()

@app.get("/instagram/callback")
async def instagram_callback(request: Request):
    params = dict(request.query_params)
    # log to stdout so Render will capture it
    print("Instagram callback params:", params)
    return {"status": "success", "params": params}
