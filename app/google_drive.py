import httplib2

from oauth2client.client import flow_from_clientsecrets, AccessTokenCredentials
from oauth2client.file import Storage
from oauth2client.tools import run_flow

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

from urllib.parse import urlencode
import requests
from urllib.request import urlopen
import json
import io



def refresh_access_token():
# You can also read these values from the json file
    client_id = "1046268304824-csvkaoqhip7ro82vd7tb7iffgvcq1l0v.apps.googleusercontent.com"
    client_secret = "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"
    refresh_token = "1//0eczud2ZYyELmCgYIARAAGA4SNwF-L9IraoskkZ28hZbr67igyok17YCQehx0tRQBp5rximNGfwccFSM2mLCMCnU9ZZrY8h5s8Mk"
    params = {
                "grant_type": "refresh_token",
                "client_id": client_id,
                "client_secret": client_secret,
                "refresh_token": refresh_token
        }

    authorization_url = "https://www.googleapis.com/oauth2/v4/token"

    r = requests.post(authorization_url, data=params)

    if r.ok:
        return r.json()['access_token']
    else:
        return None



def get_credentials(access_token):
    user_agent = "Google Sheets API for Python"
    revoke_uri = "https://accounts.google.com/o/oauth2/revoke"
    credentials = AccessTokenCredentials(
                                    access_token=access_token,
                                    user_agent=user_agent,
                                    revoke_uri=revoke_uri)
    return credentials



def updateFile(file_name, file_id):

    access_token = refresh_access_token()

    credentials = get_credentials(access_token)
    http = credentials.authorize(httplib2.Http())
    drive_service = build('drive', 'v3', http=http)


    file_metadata = {
    'name': file_name,
    'mimeType': '*/*'
    }
    media = MediaFileUpload(file_name,
                            mimetype='*/*',
                            resumable=True)
    file = drive_service.files().update(body=file_metadata, 
                                        media_body=media,
                                        fileId =  file_id, 
                                        addParents = '1POG-erqU5swFWkI8t5TF-_-tOBVQELJ9', 
                                        fields='id, parents').execute()
    print ('File ID: ' + file.get('id'))

def downloadFile(local_file_name, file_id):

    access_token = refresh_access_token()

    credentials = get_credentials(access_token)
    http = credentials.authorize(httplib2.Http())
    drive_service = build('drive', 'v3', http=http)

    request = drive_service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("{} downloaded {}%".format(local_file_name, status.progress() * 100))

    fh.seek(0)
    with open(local_file_name, 'wb') as f:
        f.write(fh.read())
        f.close()

# updataFile('user.json')

# downloadFile(log_file_id, 'log.json')


