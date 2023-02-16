from django.db import models

from apiclient.discovery import build

import httplib2,os

from google_auth_oauthlib.flow import InstalledAppFlow
from apiclient.discovery import build

# YOUTUBE_API_Key = 'AIzaSyD-ohN5V0dlXYHjP7lSrUgKcCgXDkjpR14'
YOUTUBE_API_KEY = 'AIzaSyCSZDXmnKDlNZMy8-P7EZOK44XmHWr9Y_w'


CLIENT_SECRETS_FILE = 'client_secret.json'

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account.
SCOPES = ["https://www.googleapis.com/auth/youtube"]
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

import pickle
from google.auth.transport.requests import Request

from django.db import models

def get_authenticated_service():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, credentials=creds)

# youtube_with_auth = get_authenticated_service()
youtube_with_key = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)