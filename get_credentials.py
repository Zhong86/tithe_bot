from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os

SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_creds():
    creds = None
    
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as f:
            creds = pickle.load(f)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'oauth_credentials.json',  # ← the file you downloaded from Google Cloud
                SCOPES
            )
            creds = flow.run_local_server(port=0)
        
        with open('token.pickle', 'wb') as f:
            pickle.dump(creds, f)
    
    return creds

creds = get_creds()
print('✅ Token saved to token.pickle')
print('📧 Authenticated as:', creds.token)