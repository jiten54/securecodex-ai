from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.domain.entities.job import JobStatus

class JobResponse(BaseModel):
    id: int
    file_id: int
    status: JobStatus
    level: str
    result_path: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
