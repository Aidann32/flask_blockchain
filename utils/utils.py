import os


def create_folder_and_file(folder_path: str, file_path: str):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            file.write("This is a new file.")