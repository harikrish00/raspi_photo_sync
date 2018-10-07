from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from apiclient import errors
from apiclient.http import MediaIoBaseDownload
import io
import os
from datetime import datetime
import shutil

# If modifying these scopes, delete the file token.json.
# SCOPES = 'https://www.googleapis.com/auth/drive.metadata.readonly'
SCOPES = ['https://www.googleapis.com/auth/drive']

ROOT_PATH = os.path.join(os.getcwd(),'AviPics')
BACKUP_PATH = os.path.join(ROOT_PATH,'backup')

def download_files(service, files_list):
    today = datetime.now()
    copy_dest = os.path.join(BACKUP_PATH,today.strftime('%Y%m%d'))
    os.mkdir(copy_dest)    
    for fid in files_list:
        file_meta = service.files().get(fileId=fid).execute()
        request = service.files().get_media(fileId=fid)
        download_path = os.path.join(ROOT_PATH,file_meta['title'])
        copy_path = os.path.join(BACKUP_PATH,file_meta['title'])
        print "download_path:",download_path
        print "copy_path:",copy_path
        print "File Size:",file_meta['fileSize']
        fh = io.FileIO(download_path,'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print "Download %d%%." % int(status.progress() * 100)
        shutil.copyfile(download_path,copy_path)
# PENDING
'''
Create a dated folder (do this for upto 10 days)
Download and copy the files to both main folder(AviPics) and dated folder(10062018).
Check the filename and size to be correct
Delete the files from google drive
Delete the folder older than 10 days
'''

def print_files_in_folder(service, folder_id):
  """Print files belonging to a folder.

  Args:
    service: Drive API service instance.
    folder_id: ID of the folder to print files from.
  """
  files_list = []
  page_token = None
  while True:
    try:
      param = {}
      if page_token:
        param['pageToken'] = page_token
      children = service.children().list(
          folderId=folder_id, **param).execute()

      for child in children.get('items', []):
        print child
        print 'File Id: %s' % child['id']
        files_list.append(child['id'])
      page_token = children.get('nextPageToken')
      if not page_token:
        return files_list
    except errors.HttpError, error:
      print 'An error occurred: %s' % error
      break


def main():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('drive', 'v2', http=creds.authorize(Http()))
    files_list = print_files_in_folder(service,'1Xy6wJozhJwLcsKKfNYASxDxBBbEHZoNy')
    if len(files_list) > 0:
        download_files(service,files_list)
    else:
        print "No files to download"

    # Call the Drive v3 API
    # results = service.files().list(q="mimeType='application/vnd.google-apps.folder' and 'AviPics' in parents",
    #     pageSize=10, fields="nextPageToken, files(id, name)").execute()
    # results = service.children.list(folderId='1Xy6wJozhJwLcsKKfNYASxDxBBbEHZoNy')
    # items = results.get('files', [])

    # if not items:
    #     print('No files found.')
    # else:
    #     print('Files:')
    #     for item in items:
    #         print('{0} ({1})'.format(item['name'], item['id']))

if __name__ == '__main__':
    main()