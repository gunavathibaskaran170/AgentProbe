from __future__ import annotations

from sqlalchemy import JSON, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class TestCase(Base):
    __tablename__ = "test_cases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    domain: Mapped[str] = mapped_column(String, nullable=False)
    question: Mapped[str] = mapped_column(String, nullable=False)
    expected_info: Mapped[str] = mapped_column(String, nullable=False)
    must_contain: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    must_not_contain: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    reference_text: Mapped[str] = mapped_column(String, nullable=False)


class Run(Base):
    __tablename__ = "runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    version_label: Mapped[str] = mapped_column(String, nullable=False)
    chatbot_url: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default="completed")
    results: Mapped[list[Result]] = relationship(
        back_populates="run",
        cascade="all, delete-orphan",
    )


class Result(Base):
    __tablename__ = "results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    run_id: Mapped[int] = mapped_column(
        ForeignKey("runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    run: Mapped[Run] = relationship(back_populates="results")
    test_id: Mapped[int] = mapped_column(Integer, nullable=False)
    answer: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    reason: Mapped[str] = mapped_column(String, nullable=False, default="")
    evidence: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    checks: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
