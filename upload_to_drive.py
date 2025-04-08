from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os

# Load credentials from the JSON key file (replace with your actual JSON file)
SERVICE_ACCOUNT_FILE = "service_account.json" 

# Define the Google Drive folder ID where files will be stored
FOLDER_ID = "1Rbewt_olwEAP1bfuWhp7XSCBmXxGacdP"

# Authenticate using service account
credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=["https://www.googleapis.com/auth/drive"])

# Build the Drive API client
drive_service = build("drive", "v3", credentials=credentials)

def upload_file_to_drive(file_path, file_name):
    """Uploads a file to Google Drive."""
    
    file_metadata = {
        "name": file_name,
        "parents": [FOLDER_ID]
    }
    
    media = MediaFileUpload(file_path, resumable=True) # type: ignore
    
    uploaded_file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"
    ).execute()

    print(f"File uploaded successfully! File ID: {uploaded_file.get('id')}")

# Example usage
upload_file_to_drive("test_file.txt", "uploaded_test_file.txt")
