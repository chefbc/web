import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

class DriveClient:
    def __init__(self, credentials_path=None, token_path="token.pickle"):
        self.credentials_path = credentials_path or os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        self.token_path = token_path
        self.service = None

    def authenticate(self):
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first time.
        if os.path.exists(self.token_path):
            with open(self.token_path, "rb") as token:
                creds = pickle.load(token)
        
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                # Try Service Account first if available
                if self.credentials_path and os.path.exists(self.credentials_path):
                    creds = service_account.Credentials.from_service_account_file(
                        self.credentials_path, scopes=SCOPES
                    )
                else:
                    # Fallback to OAuth2 flow (requires client_secret.json)
                    secret_path = os.environ.get("GOOGLE_CLIENT_SECRET_JSON", "client_secret.json")
                    if os.path.exists(secret_path):
                        flow = InstalledAppFlow.from_client_secrets_file(secret_path, SCOPES)
                        creds = flow.run_local_server(port=0)
                        # Save the credentials for the next run
                        with open(self.token_path, "wb") as token:
                            pickle.dump(creds, token)
                    else:
                        raise Exception("No Google Drive credentials found (Service Account or OAuth2).")

        self.service = build("drive", "v3", credentials=creds)

    def list_folders(self, parent_id):
        folders = []
        page_token = None
        query = f"'{parent_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        
        while True:
            results = self.service.files().list(
                q=query, 
                fields="nextPageToken, files(id, name, description)",
                pageToken=page_token
            ).execute()
            folders.extend(results.get("files", []))
            page_token = results.get("nextPageToken")
            if not page_token:
                break
        return folders

    def list_files(self, folder_id):
        files = []
        page_token = None
        query = f"'{folder_id}' in parents and trashed = false"
        
        while True:
            results = self.service.files().list(
                q=query, 
                fields="nextPageToken, files(id, name, description, mimeType, webContentLink, webViewLink)",
                pageToken=page_token
            ).execute()
            files.extend(results.get("files", []))
            page_token = results.get("nextPageToken")
            if not page_token:
                break
        return files
