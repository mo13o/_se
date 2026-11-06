import uuid
from datetime import date, datetime, timezone
from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class Task(Base):
    __tablename__ = "tasks"
    __table_args__ = (
        CheckConstraint("category IN ('assignment','exam','project','other')", name="ck_tasks_category"),
        CheckConstraint("priority IN ('high','medium','low')", name="ck_tasks_priority"),
        CheckConstraint("status IN ('todo','done')", name="ck_tasks_status"),
        Index("ix_tasks_status_due_date", "status", "due_date"),
        Index("ix_tasks_category", "category"),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    course_id: Mapped[str | None] = mapped_column(ForeignKey("courses.id", ondelete="SET NULL"), nullable=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    category: Mapped[str] = mapped_column(String(20), nullable=False, default="assignment")
    priority: Mapped[str] = mapped_column(String(10), nullable=False, default="medium")
    status: Mapped[str] = mapped_column(String(10), nullable=False, default="todo")
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    legacy_source_id: Mapped[int | None] = mapped_column(nullable=True, unique=True)


