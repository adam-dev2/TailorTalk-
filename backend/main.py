from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
from pydantic import BaseModel
from agent import run_agent
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from fastapi.responses import RedirectResponse 
import json, urllib.parse

import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1' 


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    user_input: str
    token: dict 

@app.head("/")
def head():
    return Response(status_code=200)

@app.get("/")
def root():
    return {"message": "✅ TailorTalk API is live"}

@app.get("/login")
def login():
    flow = Flow.from_client_secrets_file(
        "credentials.json",
        scopes=["https://www.googleapis.com/auth/calendar"],
        redirect_uri="https://tailortalk-qbst.onrender.com/oauth2callback" 
    )
    auth_url, _ = flow.authorization_url(
        prompt="consent",
        access_type="offline",
        include_granted_scopes="true"
    )
    return RedirectResponse(auth_url)


@app.get("/oauth2callback")
def oauth2callback(request: Request):
    flow = Flow.from_client_secrets_file(
        "credentials.json",
        scopes=["https://www.googleapis.com/auth/calendar"],
        redirect_uri="https://tailortalk-qbst.onrender.com/oauth2callback"
    )
    flow.fetch_token(authorization_response=str(request.url))

    creds = flow.credentials
    token_data = {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': creds.scopes
    }

    token_str = urllib.parse.quote(json.dumps(token_data))
    redirect_url = f"https://tailortalkai.streamlit.app/?token={token_str}"

    return RedirectResponse(url=redirect_url)


@app.get("/get-token")
def get_token(request: Request):
    token = request.cookies.get("google_token")
    if not token:
        return JSONResponse(status_code=401, content={"error": "Unauthorized"})
    return JSONResponse(content={"token": json.loads(token)})


@app.post("/chat")
def chat_with_agent(message: Message):
    reply = run_agent(message.user_input, message.token)
    return {"reply": reply}
