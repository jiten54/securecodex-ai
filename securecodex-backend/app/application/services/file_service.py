import os
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from app.infrastructure.repositories.file_repository import FileRepository
from app.infrastructure.storage.file_storage import FileStorage
from app.core.config import settings

class FileService:
    ALLOWED_EXTENSIONS = {".py", ".js"}

    def __init__(self, db: Session):
        self.file_repo = FileRepository(db)
        self.storage = FileStorage()

    def upload_file(self, file: UploadFile, user_id: int):
        """Handle file validation, storage, and metadata recording."""
        # Validate file extension
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in self.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type. Allowed: {', '.join(self.ALLOWED_EXTENSIONS)}"
            )

        # Validate file size
        file.file.seek(0, os.SEEK_END)
        file_size = file.file.tell()
        file.file.seek(0)
        if file_size > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Max size: {settings.MAX_FILE_SIZE / (1024 * 1024)}MB"
            )

        # Save file to storage
        file_path = self.storage.save_file(file)

        # Save metadata to DB
        return self.file_repo.create_file_record(
            filename=file.filename,
            filepath=file_path,
            file_type=file_ext,
            user_id=user_id
        )
