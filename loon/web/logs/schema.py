from datetime import datetime

from pydantic import BaseModel


class LogEntryResponse(BaseModel):
    id: int
    log_type: str
    created_at: datetime
    message: str
