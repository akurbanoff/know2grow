import datetime
from io import BytesIO
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import json
import os
from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google.auth.transport.requests import Request


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

        pickle_file = f'./google_drive/token_{API_SERVICE_NAME}_{API_VERSION}.json'
        # print(pickle_file)

        if os.path.exists(pickle_file):
            with open(pickle_file, 'rb') as token:
                cred = json.load(token)
                GoogleDrive.cred = cred

        if not cred or not cred.valid:
            if cred and cred.expired and cred.refresh_token:
                cred.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
                cred = flow.run_local_server()
                GoogleDrive.cred = cred

            with open(pickle_file, 'wb') as token:
                json.dump(cred, token)

        try:
            service = build(API_SERVICE_NAME, API_VERSION, credentials=GoogleDrive.cred)
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


    def upload_files(self, filename: str, mime_type: str, file_content, folder_id: str = ''):
        # file_metadata = {
        #     'name': filename,
        #     'parents': [folder_id]
        # }
        #
        # media = MediaFileUpload(BytesIO(file_content), filename=filename, mimetype=mime_type)
        #
        # drive.files().create(
        #     body=file_metadata,
        #     media_body=media,
        #     fields='id'
        # ).execute()
        try:
            #service = build('drive', 'v3', credentials=GoogleDrive.cred)

            file_metadata = {'name': filename, 'content': file_content, 'parents': [folder_id]}
            media = MediaFileUpload(filename,
                                    mimetype=mime_type)
            # pylint: disable=maybe-no-member
            file = self.files().create(body=file_metadata, media_body=media,
                                          fields='id').execute()
            print(F'File ID: {file.get("id")}')

        except HttpError as error:
            print(F'An error occurred: {error}')
            file = None

        return file.get('id')
