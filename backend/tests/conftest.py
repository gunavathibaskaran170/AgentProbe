from __future__ import annotations

import os
import shutil
import tempfile
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# These must run before app.db / app.main are imported: the database URL is
# read once at import time. Using a fresh temporary directory guarantees the
# tests can never read or write backend/agentprobe.db.
_TEST_DIR = Path(tempfile.mkdtemp(prefix="agentprobe-test-"))
os.environ["AGENTPROBE_DATABASE_URL"] = (
    f"sqlite:///{(_TEST_DIR / 'agentprobe_test.db').as_posix()}"
)

from sqlalchemy.orm import Session  # noqa: E402

from app import models  # noqa: E402,F401
from app.db import Base, SessionLocal, engine, get_db  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture()
def client() -> Iterator[TestClient]:
    """A TestClient backed by a clean, temporary SQLite database."""
    Base.metadata.create_all(bind=engine)

    def override_get_db() -> Iterator[Session]:
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session", autouse=True)
def cleanup_temporary_database() -> Iterator[None]:
    yield
    engine.dispose()
    shutil.rmtree(_TEST_DIR, ignore_errors=True)
