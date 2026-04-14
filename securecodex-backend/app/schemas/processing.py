from pydantic import BaseModel
from typing import Optional

class ProcessRequest(BaseModel):
    level: Optional[str] = "medium"
