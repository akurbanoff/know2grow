from drive.client import Client
from src.file_work import FileWork

client = Client(credentials_path='./google_drive/know2grow-secret-key.json') #./google_drive/

# d = client.root()
#d.create_folder(name='know2grow')
# know2grow = d.get_or_create_folder(name='know2grow')
# for i in d.list():
#     print(i.name)
#     for j in i.list():
#         print(j.name)


class Drive:
    def __init__(self):
        self.drive = client
        self.client_root = client.root()
        self.file_work = FileWork()

    def get_file_by_name(self, name):
        return self.drive.get_file_by_name(name=name, parent_id='1pMx7TQI03bfbBUnuPVJVuMtKk2D88scp')

    def upload_file(self,  name, mime_type, file, parent_dir_id = '1pMx7TQI03bfbBUnuPVJVuMtKk2D88scp'):
        self.file_work.create_file(file=file, filename=name)
        self.drive.upload_file(
            parent_id=parent_dir_id, name=name, mime_type=mime_type, path=f'../media/{name}'
        )
        self.file_work.delete_file(filename=name)

        return 200

    def get_all_files(self):
        files = {}
        for dir in self.client_root.list():
            for file in dir.list():
                files[file.name] = file

        return files

drive = Drive()