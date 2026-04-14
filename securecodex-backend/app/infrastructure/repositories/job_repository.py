from sqlalchemy.orm import Session
from app.domain.entities.job import Job, JobStatus
from typing import Optional

class JobRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_job(self, file_id: int, level: str = "medium") -> Job:
        """Create a new job record."""
        db_job = Job(file_id=file_id, status=JobStatus.PENDING, level=level)
        self.db.add(db_job)
        self.db.commit()
        self.db.refresh(db_job)
        return db_job

    def update_job_status(self, job_id: int, status: JobStatus, result_path: Optional[str] = None, error_message: Optional[str] = None) -> Job:
        """Update the status and result of a job."""
        db_job = self.db.query(Job).filter(Job.id == job_id).first()
        if db_job:
            db_job.status = status
            if result_path:
                db_job.result_path = result_path
            if error_message:
                db_job.error_message = error_message
            self.db.commit()
            self.db.refresh(db_job)
        return db_job

    def get_job_by_id(self, job_id: int) -> Optional[Job]:
        """Fetch a job by ID."""
        return self.db.query(Job).filter(Job.id == job_id).first()
