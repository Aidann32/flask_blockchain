import os
import hashlib

from docx import Document


def calculate_file_hash(file_path: str, algorithm='sha256'):
    """Calculate the hash of a file."""
    hash_algorithm = hashlib.new(algorithm)
    with open(file_path, 'rb') as f:
        while True:
            data = f.read(65536)  # Read in chunks of 64KB
            if not data:
                break
            hash_algorithm.update(data)
    return hash_algorithm.hexdigest()


def create_folder_and_file(folder_path: str, file_path: str):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            file.write("This is a new file.")


def extract_text_from_docx(file):
    document = Document(file)
    text = ""
    for paragraph in document.paragraphs:
        text += paragraph.text + "\n"
    return text
