from googleapiclient.discovery import build
from app.oauth import build_credentials

def get_recent_emails(n=5):
    creds = build_credentials()
    if not creds:
        return {"error": "No credentials"}
    
    service = build("gmail", "v1", credentials=creds)
    results = service.users().messages().list(userId='me', maxResults=n).execute()
    messages = results.get("messages", [])
    
    email_data = []
    for msg in messages:
        full_msg = service.users().messages().get(userId='me', id=msg["id"]).execute()
        headers = full_msg.get("payload", {}).get("headers", [])
        snippet = full_msg.get("snippet", "")
        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "(No Subject)")
        from_field = next((h["value"] for h in headers if h["name"] == "From"), "(Unknown)")
        email_data.append({"from": from_field, "subject": subject, "snippet": snippet})
    return email_data


