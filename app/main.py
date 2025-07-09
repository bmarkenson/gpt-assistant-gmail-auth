from flask import Blueprint, jsonify, redirect, session, url_for, request, abort
from app.oauth import get_flow, login_required
from app.gmail import get_recent_emails
from google.cloud import secretmanager
import os

def get_api_key():
    project_id = os.environ["GCP_PROJECT_ID"]
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/custom-gpt-api-key/versions/latest"
    response = client.access_secret_version(name=name)
    return response.payload.data.decode("UTF-8")

main_bp = Blueprint("main", __name__)

@main_bp.before_request
def check_api_key():
    # Skip auth for the OAuth redirect endpoints
    if request.endpoint in ("main.authorize", "main.oauth2callback"):
        return

    expected = get_api_key()
    received = request.headers.get("X-API-Key")
    if received != expected:
        abort(403)

@main_bp.route("/authorize")
def authorize():
    flow = get_flow()
    auth_url, _ = flow.authorization_url(prompt="consent", access_type="offline", include_granted_scopes="true")
    return redirect(auth_url)

@main_bp.route("/oauth2callback")
def oauth2callback():
    flow = get_flow()
    flow.fetch_token(authorization_response=request.url)
    creds = flow.credentials
    session["token"] = {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": creds.scopes
    }
    return redirect(url_for("main.read_email"))

@main_bp.route("/read_email", methods=["GET"])
#@login_required
def read_email():
    n = int(request.args.get("n", 5))
    data = get_recent_emails(n)
    return jsonify(data)

@main_bp.route("/debug/refresh_token")
def debug_refresh_token():
    token = session.get("token")
    return jsonify({"refresh_token": token.get("refresh_token")})



