from __future__ import annotations

import os
from pathlib import Path
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

BACKEND_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = BACKEND_DIR / "agentprobe.db"
DEFAULT_DATABASE_URL = f"sqlite:///{DEFAULT_DB_PATH.as_posix()}"


def get_database_url() -> str:
    """Return the configured database URL, defaulting to backend/agentprobe.db."""
    return os.environ.get("AGENTPROBE_DATABASE_URL", DEFAULT_DATABASE_URL)


DATABASE_URL = get_database_url()

_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=_connect_args, future=True)
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    class_=Session,
)


class Base(DeclarativeBase):
    """Declarative base shared by every model."""


def create_tables() -> None:
    """Create all mapped tables on the configured database."""
    # Import here so model metadata is registered before create_all runs even
    # when this function is called from a context that did not import models.
    from app import models  # noqa: F401

    Base.metadata.create_all(bind=engine)


def get_db() -> Iterator[Session]:
    """FastAPI dependency yielding one database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
