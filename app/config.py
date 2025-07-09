import os

class Config:
    SECRET_KEY = os.environ.get("FLASK_SECRET", "dev")
    CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
    CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
    REDIRECT_URI = os.environ.get("GOOGLE_REDIRECT_URI", "http://localhost:5000/oauth2callback")
    SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


