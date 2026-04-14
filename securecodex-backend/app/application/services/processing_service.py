from sqlalchemy.orm import Session
from app.infrastructure.repositories.job_repository import JobRepository
from app.infrastructure.repositories.file_repository import FileRepository
from app.workers.tasks import process_file_task
from fastapi import HTTPException, status

class ProcessingService:
    def __init__(self, db: Session):
        self.job_repo = JobRepository(db)
        self.file_repo = FileRepository(db)

    def trigger_processing(self, file_id: int, user_id: int, level: str = "medium"):
        """Trigger the background processing for a file."""
        # Verify file exists and belongs to user
        file_record = self.file_repo.get_file_by_id(file_id)
        if not file_record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
        
        if file_record.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to process this file")

        # Create job record
        job = self.job_repo.create_job(file_id, level=level)
        
        # Trigger Celery task
        process_file_task.delay(job.id, file_id, level)
        
        return job

    def get_job_status(self, job_id: int, user_id: int):
        """Get the status of a processing job."""
        job = self.job_repo.get_job_by_id(job_id)
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
            
        # Verify ownership via the file
        file_record = self.file_repo.get_file_by_id(job.file_id)
        if file_record.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this job")
            
        return job
