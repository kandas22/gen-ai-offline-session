import os
import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from app.config import Config

class GmailService:
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    
    def __init__(self):
        self.client_id = Config.GOOGLE_CLIENT_ID
        self.client_secret = Config.GOOGLE_CLIENT_SECRET
        
        # In a real app, you'd load this from a file or env var properly
        self.client_config = {
            "web": {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        }

    def get_authorization_url(self, redirect_uri):
        flow = google_auth_oauthlib.flow.Flow.from_client_config(
            self.client_config,
            scopes=self.SCOPES
        )
        flow.redirect_uri = redirect_uri
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        return authorization_url, state

    def get_credentials_from_code(self, code, redirect_uri):
        flow = google_auth_oauthlib.flow.Flow.from_client_config(
            self.client_config,
            scopes=self.SCOPES
        )
        flow.redirect_uri = redirect_uri
        flow.fetch_token(code=code)
        return flow.credentials

    def get_service(self, credentials):
        return build('gmail', 'v1', credentials=credentials)

    def list_messages(self, service, query=''):
        results = service.users().messages().list(userId='me', q=query).execute()
        messages = results.get('messages', [])
        return messages

    def get_message(self, service, msg_id):
        message = service.users().messages().get(userId='me', id=msg_id).execute()
        return message
