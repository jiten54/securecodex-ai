from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.infrastructure.database.session import get_db
from app.application.services.processing_service import ProcessingService
from app.api.dependencies.auth import get_current_user
from app.domain.entities.user import User
from app.schemas.job import JobResponse
from app.schemas.processing import ProcessRequest

from app.api.dependencies.rate_limit import rate_limit

router = APIRouter(tags=["Processing"])

@router.post("/process/{file_id}", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED, dependencies=[Depends(rate_limit(limit=10, window=60))])
async def process_file(
    file_id: int,
    request: ProcessRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Trigger obfuscation processing for a specific file."""
    processing_service = ProcessingService(db)
    return processing_service.trigger_processing(file_id, current_user.id, level=request.level)

@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job_status(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Check the status of a processing job."""
    processing_service = ProcessingService(db)
    return processing_service.get_job_status(job_id, current_user.id)
