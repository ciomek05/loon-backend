from fastapi import APIRouter
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select
from starlette.requests import Request

from loon.web.auth.middleware import admin
from loon.web.db import engine
from loon.web.logs.models import LogEntry
from loon.web.logs.schema import LogEntryResponse

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/logs", response_model=list[LogEntryResponse])
@admin
async def list_logs(request: Request):
    with Session(engine) as session:
        statement = (
            select(LogEntry)
            .options(selectinload(LogEntry.log_type))
            .order_by(LogEntry.created_at)
        )
        entries = session.exec(statement).all()
        return [
            LogEntryResponse(
                id=entry.id,
                log_type=entry.log_type.code,
                created_at=entry.created_at,
                message=entry.message,
            )
            for entry in entries
        ]
