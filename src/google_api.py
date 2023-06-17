import json

from drive import Client
from fastapi_cache.decorator import cache

from src.file_work import FileWork


class Drive:
    client = Client(credentials_path='./src/know2grow-secret-key.json')

    def __init__(self):
        self.drive = Drive.client
        self.client_root = Drive.client.root()
        self.file_work = FileWork()

    def get_file_by_name(self, name):
        return self.drive.get_file_by_name(name=name, parent_id='1pMx7TQI03bfbBUnuPVJVuMtKk2D88scp')

    def upload_file(self,  name, mime_type, file, parent_dir_id = '1pMx7TQI03bfbBUnuPVJVuMtKk2D88scp'):
        self.file_work.create_file(file=file, filename=name)
        self.drive.upload_file(
            parent_id=parent_dir_id, name=name, mime_type=mime_type, path=f'./media/{name}'
        )
        self.file_work.delete_file(filename=name)

        return 200

    @cache(expire=60)
    def get_all_files(self):
        files = {}
        for dir in self.client_root.list():
            for file in dir.list():
                files[file.name] = file
        return files

    def delete_file(self, filename):
        for dir in self.client_root.list():
            for file in dir.list():
                if file.name == filename:
                    file.unlink()
                    return 200
        return f'Имя файла - {filename} неправильное. Имя файла вводится вместе с его форматом(filename.png)'

drive = Drive()
# d = drive.client_root
# for i in d.list():
#     print(i.name)
#     for j in i.list():
#         print(j.name)