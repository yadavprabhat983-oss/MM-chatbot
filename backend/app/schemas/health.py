import datetime
from pydantic import BaseModel
from typing import Optional

class HealthResponse(BaseModel):
    status: str
    app_env: str
    timestamp: datetime.datetime

class ReadinessResponse(BaseModel):
    status: str
    database: str
    pgvector_supported: bool
    error: Optional[str] = None
    timestamp: datetime.datetime
