from fastapi import UploadFile
import os


class FileWork:
    def create_file(self, file: UploadFile):
        file_path = f'../media/{file.filename}'
        with open(file_path, 'wb') as f:
            f.write(file.file.read())

        return 200

    def get_file(self, filename):
        file_path = f'../media/{filename}'
        if os.path.isfile(file_path):
            with open(file_path, 'rb') as f:
                file = f.read()
            return file
        else:
            return 'Такого файла нет.'