from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.http import MediaFileUpload
import io
import json
from datetime import datetime
import os 
def ConectarseDrive(dir_folder_credentials = '.'):
    SCOPES = ['https://www.googleapis.com/auth/drive']
    path_credentials = os.path.join(dir_folder_credentials, 'credentials.json')
    # with open(path_credentials, 'r') as f:
    SERVICE_ACCOUNT_FILE = path_credentials
    print(SERVICE_ACCOUNT_FILE)
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    service = build('drive', 'v3', credentials=credentials)
    return service

def ObtenerIdArchivos(service, FOLDER_ID, pageSize=50):
    results = service.files().list(
        q=f"'{FOLDER_ID}' in parents",
        pageSize=pageSize,
        fields="files(id, name)"    
    ).execute()
    items = results.get('files', [])
    return items

def DescargarArchivo(service, download_file_path, file_id):
    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(download_file_path, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
        print(f"Descargando... {int(status.progress() * 100)}% completado.")
    print(f"Archivo descargado como {download_file_path}.")

def SubirArchivo(service, upload_folder_id, upload_file_path, upload_file_name):
    file_metadata = {
        'name': upload_file_name,
        'parents': [upload_folder_id]
    }
    media = MediaFileUpload(upload_file_path, resumable=True)
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()
    print(f"Archivo subido. ID del archivo: {file.get('id')}")
    
def CrearCarpeta(service, new_folder_name, parent_folder_id): 
    folder_metadata = {
        # 'name': 'Test_sub_carpeta',
        'name': new_folder_name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_folder_id]
    }
    folder = service.files().create(body=folder_metadata, fields='id').execute()
    print(f"Subcarpeta creada con ID: {folder.get('id')}")
    return folder.get('id')

def SubirCSVs(dir_folder_credentials: str, master_drive_key: str, owner_data: str, path_dict: list):
    if dir_folder_credentials:
        service = ConectarseDrive(dir_folder_credentials)
        curret_date = path_dict['timestamp']
        path_data = path_dict['files']
        folder_data_id = CrearCarpeta(service=service, new_folder_name=owner_data + curret_date, parent_folder_id=master_drive_key)
        for (path, name_file) in path_data:
            SubirArchivo(service=service, upload_folder_id=folder_data_id, upload_file_path=path, upload_file_name=name_file)
        folder_link = f"https://drive.google.com/drive/folders/{folder_data_id}"
        return folder_link
    return ""