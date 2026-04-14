import os
from app.workers.celery_app import celery_app
from app.infrastructure.database.session import SessionLocal
from app.infrastructure.repositories.file_repository import FileRepository
from app.infrastructure.repositories.job_repository import JobRepository
from app.domain.entities.job import JobStatus
from app.infrastructure.storage.file_storage import FileStorage
from app.application.services.obfuscator import Obfuscator

@celery_app.task(name="process_file_task")
def process_file_task(job_id: int, file_id: int, level: str = "medium"):
    """Background task to process a file for obfuscation."""
    db = SessionLocal()
    job_repo = JobRepository(db)
    file_repo = FileRepository(db)
    storage = FileStorage()
    
    try:
        # Update status to processing
        job_repo.update_job_status(job_id, JobStatus.PROCESSING)
        
        # Fetch file metadata
        file_record = file_repo.get_file_by_id(file_id)
        if not file_record:
            raise Exception(f"File with ID {file_id} not found")
            
        # Read the file content
        with open(file_record.filepath, "r") as f:
            content = f.read()
            
        # Apply real obfuscation using the Obfuscator service
        obfuscator = Obfuscator(level=level)
        obfuscated_content = obfuscator.obfuscate(content)
        
        # Save processed file using storage service
        result_path = storage.save_processed_file(obfuscated_content, file_record.filename)
            
        # Update job status to completed
        job_repo.update_job_status(job_id, JobStatus.COMPLETED, result_path=result_path)
        
    except Exception as e:
        # Update job status to failed
        job_repo.update_job_status(job_id, JobStatus.FAILED, error_message=str(e))
    finally:
        db.close()
