import datetime
import pickle
from io import BytesIO

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import json
import os
from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google.auth.transport.requests import Request
from re import search


class GoogleDrive:
    mime_types = {
        '.jpeg': 'image/jpeg',
        '.jpg': 'image/jpeg'
    }
    cred = None
    @staticmethod
    def create_drive():
        CLIENT_SECRET_FILE = '/home/neekee/PyCharm Projects/know2grow/client_secret_1079250209238-ugnen9qhn3f7s43cl1ur0tigqdcinimg.apps.googleusercontent.com.json'
        API_SERVICE_NAME = 'drive'
        API_VERSION = 'v3'
        SCOPES = 'https://www.googleapis.com/auth/drive'
        print(SCOPES)

        cred = None

        #pickle_file = f'./google_drive/token_{API_SERVICE_NAME}_{API_VERSION}.pickle'
        json_file = './google_drive/token.json'
        # print(pickle_file)

        if os.path.exists(json_file):
            cred = Credentials.from_authorized_user_file(json_file, SCOPES)

        if not cred or not cred.valid:
            if cred and cred.expired and cred.refresh_token:
                cred.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
                cred = flow.run_local_server(port=0)

            with open(json_file, 'w') as token:
                token.write(cred.to_json())

        try:
            service = build(API_SERVICE_NAME, API_VERSION, credentials=cred)
            print(API_SERVICE_NAME, 'service created successfully')
            return service
        except Exception as e:
            print('Unable to connect.')
            print(e)
            return None

    @staticmethod
    def convert_to_RFC_datetime(year=1900, month=1, day=1, hour=0, minute=0):
        dt = datetime.datetime(year, month, day, hour, minute, 0).isoformat() + 'Z'
        return dt


    def get_files(self, id, filename: str, mime_type: str, size, folder_id: str = ''):
        res = self.files().list(
            fields=f"nextPageToken, files({id}, {filename}, {mime_type}, {size}, {folder_id}, modifiedTime)"
        )
        items = res.get('files', [])

        return items

    def upload_files(self, filename: str, mime_type: str, file_content, folder_id: str = ''):
        file_metadata = {
            'name': filename,
            'content': file_content,
            'mimeType': mime_type,
            'parents': [folder_id]
        }

        media = MediaFileUpload(filename, resumable=True)
        file = self.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()

        return 'Файл удачно загружен!'

    # def download(self, filename: str):
    #     search_result = search(self, query=f'name={filename}')
    #
    #     file_id = search_result[0][0]
    #     self.permissions().create(
    #         body={'role': 'reader', 'type': 'anyone'},
    #         fileId=file_id
    #     ).execute()
