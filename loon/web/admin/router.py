from fastapi import APIRouter
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select
from starlette.requests import Request

from loon.web.auth.middleware import admin
from loon.web.db import engine
from loon.web.logs.models import LogEntry
from loon.web.logs.schema import LogEntryResponse
from loon.web.users.models import MinecraftUser, User
from loon.web.users.schema import MinecraftUserPublic, UserPublic

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


@router.get("/mc-users", response_model=list[MinecraftUserPublic])
@admin
async def list_mc_users(request: Request):
    with Session(engine) as session:
        statement = select(MinecraftUser).order_by(MinecraftUser.username)
        return session.exec(statement).all()


@router.get("/users", response_model=list[UserPublic])
@admin
async def list_users(request: Request):
    with Session(engine) as session:
        statement = (
            select(User)
            .options(selectinload(User.minecraft_user))
            .order_by(User.internal_username)
        )
        return session.exec(statement).all()
