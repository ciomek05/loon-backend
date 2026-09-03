import asyncio

from sqlmodel import Session, select

from loon.web.db import engine
from loon.web.logs.models import LogType, LogEntry
from loon.web.logs.types import LogTypeEnum


def _write_log(log_type: LogTypeEnum, message: str) -> None:
    with Session(engine) as session:
        statement = select(LogType).where(LogType.code == log_type.value)
        log_type_object = session.exec(statement).first()

        if not log_type_object:
            log_type_object = LogType(code=log_type.value)
            session.add(log_type_object)
            session.commit()
            session.refresh(log_type_object)

        log_entry = LogEntry(log_type_id=log_type_object.id, message=message)
        session.add(log_entry)
        session.commit()


async def write_log(log_type: LogTypeEnum, message: str) -> None:
    await asyncio.to_thread(_write_log, log_type, message)
