from sqlalchemy import String, Text, Enum, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from app.core.database import Base
from .enums import TaskPriority, TaskStatus


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped['TaskStatus'] = mapped_column(Enum(TaskStatus), default=TaskStatus.PENDING)
    priority: Mapped['TaskPriority'] = mapped_column(Enum(TaskPriority), default=TaskPriority.MEDIUM)
    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now, nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None, onupdate=datetime.now)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    user = relationship("User", back_populates="tasks")
