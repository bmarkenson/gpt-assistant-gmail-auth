from flask import redirect, request, session, url_for, current_app
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.cloud import secretmanager
import os

def get_flow():
    return Flow.from_client_config(
        {
            "web": {
                "client_id": current_app.config["CLIENT_ID"],
                "client_secret": current_app.config["CLIENT_SECRET"],
                "redirect_uris": [current_app.config["REDIRECT_URI"]],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=current_app.config["SCOPES"],
        redirect_uri=current_app.config["REDIRECT_URI"]
    )

def load_refresh_token_from_secret():
    client = secretmanager.SecretManagerServiceClient()
    project_id = os.environ["GCP_PROJECT_ID"]
    name = f"projects/{project_id}/secrets/gmail-refresh-token/versions/latest"
    response = client.access_secret_version(name=name)
    return response.payload.data.decode("UTF-8")

def build_credentials():
    refresh_token = load_refresh_token_from_secret()
    print("Loaded refresh token:", refresh_token[:8], "...")
    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ["GOOGLE_CLIENT_ID"],
        client_secret=os.environ["GOOGLE_CLIENT_SECRET"],
        scopes=["https://www.googleapis.com/auth/gmail.readonly"],
    )
    print("Refreshing access token with client ID:", os.environ["GOOGLE_CLIENT_ID"])
    creds.refresh(Request())
    return creds

def login_required(func):
    def wrapper(*args, **kwargs):
        if "token" not in session:
            return redirect(url_for("main.authorize"))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


