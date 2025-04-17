import os
import uuid
from fastapi import UploadFile
UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
def save_uploaded_file(file: UploadFile) -> str:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_ext = os.path.splitext(file.filename)[1]
    file_id = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, file_id)

    with open(file_path, "wb") as f:
        f.write(file.file.read())
    return file_path
def save_output_file(content: str, filename_no_ext: str, output_type: str) -> str:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_file = os.path.join(OUTPUT_DIR, f"{filename_no_ext}.{output_type}")
    with open(output_file, "w") as f:
        f.write(content)
    return output_file
