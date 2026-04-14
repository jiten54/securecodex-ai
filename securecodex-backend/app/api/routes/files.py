from fastapi import APIRouter, Depends, UploadFile, File, status
from fastapi.responses import FileResponse as FastAPIFileResponse
from sqlalchemy.orm import Session
from app.infrastructure.database.session import get_db
from app.application.services.file_service import FileService
from app.api.dependencies.auth import get_current_user
from app.domain.entities.user import User
from app.schemas.file import FileResponse

from app.application.services.download_service import DownloadService

from app.api.dependencies.rate_limit import rate_limit
from app.infrastructure.repositories.api_key_repository import APIKeyRepository

router = APIRouter(prefix="/files", tags=["File Management"])

@router.post("/upload", response_model=FileResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(rate_limit(limit=5, window=60))])
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload a code file (.py, .js) for obfuscation."""
    file_service = FileService(db)
    return file_service.upload_file(file, current_user.id)

@router.post("/keys", status_code=status.HTTP_201_CREATED)
async def create_api_key(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate a new API key for the current user."""
    api_key_repo = APIKeyRepository(db)
    new_key = api_key_repo.create_api_key(current_user.id)
    return {"api_key": new_key.key}

@router.get("/keys")
async def list_api_keys(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all API keys for the current user."""
    api_key_repo = APIKeyRepository(db)
    keys = api_key_repo.get_keys_by_user(current_user.id)
    return [{"id": k.id, "key": f"{k.key[:8]}...", "created_at": k.created_at} for k in keys]

@router.get("/download/{job_id}")
async def download_processed_file(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Securely download the obfuscated version of a file.
    Only the owner of the original file can download the result.
    """
    download_service = DownloadService(db)
    file_path = download_service.get_file_path(job_id, current_user.id)
    
    # Return the file as a response
    return FastAPIFileResponse(
        path=file_path,
        filename=f"obfuscated_{job_id}.py",
        media_type='application/octet-stream'
    )
