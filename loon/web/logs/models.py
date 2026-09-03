from datetime import datetime, timezone

from sqlmodel import SQLModel, Field, Relationship


class LogType(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    code: str = Field(nullable=False, unique=True)
    entries: list["LogEntry"] = Relationship(back_populates="log_type")


class LogEntry(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    log_type_id: int = Field(foreign_key="logtype.id", nullable=False)
    log_type: LogType = Relationship(back_populates="entries")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    message: str = Field(nullable=False)
