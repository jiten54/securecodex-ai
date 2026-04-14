import os
import uuid
from fastapi import UploadFile
from app.core.config import settings

class FileStorage:
    """
    Infrastructure service for handling physical file storage.
    Manages uploads and processed files.
    """
    def __init__(self):
        self.upload_dir = settings.UPLOAD_DIR
        self.processed_dir = settings.PROCESSED_DIR
        
        # Ensure directories exist
        for directory in [self.upload_dir, self.processed_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)

    def save_file(self, file: UploadFile) -> str:
        """Save an uploaded file and return its local path."""
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(self.upload_dir, unique_filename)

        with open(file_path, "wb") as buffer:
            # Read in chunks to handle large files efficiently
            while content := file.file.read(1024 * 1024):  # 1MB chunks
                buffer.write(content)

        return file_path

    def save_processed_file(self, content: str, original_filename: str) -> str:
        """Save obfuscated content to the processed directory."""
        file_extension = os.path.splitext(original_filename)[1]
        unique_filename = f"proc_{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(self.processed_dir, unique_filename)

        with open(file_path, "w") as f:
            f.write(content)

        return file_path

    def file_exists(self, path: str) -> bool:
        """Check if a file exists at the given path."""
        return os.path.exists(path)
