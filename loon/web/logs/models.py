from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from loon.web.db import Base


class LogType(Base):
    __tablename__ = "logtype"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(unique=True)
    entries: Mapped[list["LogEntry"]] = relationship(back_populates="log_type")


class LogEntry(Base):
    __tablename__ = "logentry"

    id: Mapped[int] = mapped_column(primary_key=True)
    log_type_id: Mapped[int] = mapped_column(ForeignKey("logtype.id"))
    log_type: Mapped[LogType] = relationship(back_populates="entries")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    message: Mapped[str]
