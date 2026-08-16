from sqlmodel import SQLModel, create_engine

from config import settings


def database_url(url: str | None = None) -> str:
    url = url or settings.database.url
    for src, dst in (
        ("mysql://", "mysql+pymysql://"),
        ("postgres://", "postgresql+psycopg://"),
        ("postgresql://", "postgresql+psycopg://"),
    ):
        if url.startswith(src):
            return dst + url.removeprefix(src)
    return url


url = database_url()
kwargs: dict = {}
if url.startswith("sqlite"):
    kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(url, echo=True, **kwargs)
SQLModel.metadata.create_all(engine)
