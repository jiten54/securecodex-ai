from sqlalchemy.orm import Session
from app.domain.entities.file import File

class FileRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_file_record(self, filename: str, filepath: str, file_type: str, user_id: int) -> File:
        """Create a new file record in the database."""
        db_file = File(
            filename=filename,
            filepath=filepath,
            file_type=file_type,
            user_id=user_id
        )
        self.db.add(db_file)
        self.db.commit()
        self.db.refresh(db_file)
        return db_file

    def get_file_by_id(self, file_id: int) -> File:
        """Fetch a file record by ID."""
        return self.db.query(File).filter(File.id == file_id).first()
