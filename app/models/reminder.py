from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy import String, Boolean, DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class ReminderStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    CANCELLED = "cancelled"

class Reminder(Base):
    __tablename__ = "reminders"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_phone: Mapped[str] = mapped_column(String, index=True)
    message_content: Mapped[str] = mapped_column(Text)
    trigger_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False)
    cron_pattern: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    status: Mapped[ReminderStatus] = mapped_column(
        default=ReminderStatus.PENDING, index=True
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )
