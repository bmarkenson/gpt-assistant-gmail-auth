import os
import json
import requests
from flask import Flask, redirect, request, session
from urllib.parse import urlencode
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

AUTH_BASE = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

@app.route("/")
def index():
    return '<a href="/authorize">Authorize Gmail</a>'

@app.route("/authorize")
def authorize():
    query = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",
        "prompt": "consent"
    }
    url = f"{AUTH_BASE}?{urlencode(query)}"
    print("Redirecting to:", url)
    return redirect(url)

@app.route("/oauth2callback")
def oauth2callback():
    print("Query args:", request.args)
    if "error" in request.args:
        return f"Error: {request.args['error']}"

    code = request.args.get("code")
    data = {
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code"
    }

    r = requests.post(TOKEN_URL, data=data)
    token_data = r.json()
    session["tokens"] = token_data

    return f"""
    <h3>OAuth Success</h3>
    <pre>{json.dumps(token_data, indent=2)}</pre>
    """

if __name__ == "__main__":
    app.run(debug=True)


