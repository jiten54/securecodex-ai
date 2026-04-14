from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.infrastructure.repositories.job_repository import JobRepository
from app.infrastructure.repositories.file_repository import FileRepository
from app.infrastructure.storage.file_storage import FileStorage
from app.domain.entities.job import JobStatus

class DownloadService:
    """
    Application service for handling secure file downloads.
    Enforces business rules for file access.
    """
    def __init__(self, db: Session):
        self.job_repo = JobRepository(db)
        self.file_repo = FileRepository(db)
        self.storage = FileStorage()

    def get_file_path(self, job_id: int, user_id: int) -> str:
        """
        Verify that the job is completed and belongs to the user,
        then return the path to the processed file.
        """
        # 1. Fetch job
        job = self.job_repo.get_job_by_id(job_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )

        # 2. Security: Ensure job belongs to current user
        file_record = self.file_repo.get_file_by_id(job.file_id)
        if not file_record or file_record.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this file"
            )

        # 3. Logic: Only allow if job is completed
        if job.status != JobStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File is not ready for download. Current status: {job.status}"
            )

        if not job.result_path:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Processed file path is missing"
            )

        # 4. Infrastructure: Check if file physically exists
        if not self.storage.file_exists(job.result_path):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Processed file not found on server"
            )

        return job.result_path
