from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import base64, email, requests

creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/gmail.readonly'])
service = build('gmail', 'v1', credentials=creds)

results = service.users().messages().list(userId='me', labelIds=['UNREAD'], maxResults=5).execute()
messages = results.get('messages', [])

for msg in messages:
    msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()
    payload = msg_data['payload']
    headers = payload['headers']

    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "(No Subject)")
    sender = next((h['value'] for h in headers if h['name'] == 'From'), "(Unknown Sender)")

    # Get body content safely
    body = ""
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                break
    elif 'body' in payload and 'data' in payload['body']:
        body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')

    # Fallback if body is still empty
    if not body:
        body = "(No message content)"

    print(f"Sender: {sender}, Subject: {subject}\n{body}\n")

    # Send to your FastAPI backend
    requests.post("https://7c93-152-58-205-247.ngrok-free.app/leads", json={
        "name": sender.split('<')[0].strip(),
        "email": sender.split('<')[-1].replace('>', '').strip(),
        "message": body,
        "source": "Email"
    })
