from pydantic import BaseModel
from datetime import datetime

class FileResponse(BaseModel):
    id: int
    filename: str
    status: str = "uploaded"
    created_at: datetime

    class Config:
        from_attributes = True
