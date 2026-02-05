from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse

app = FastAPI()

API_KEY = "honeypot_api_key_2026"

@app.post("/api/honeypot")
async def honeypot(
    x_api_key: str = Header(None)
):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    return JSONResponse(
        status_code=200,
        content={
            "status": "success",
            "reply": "Why is my account being suspended?"
        }
    )
