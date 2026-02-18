from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.reminder import Reminder, ReminderStatus
from datetime import datetime
from typing import Optional, List

async def create_reminder(
    db: AsyncSession,
    user_phone: str,
    message_content: str,
    trigger_time: Optional[datetime] = None,
    is_recurring: bool = False,
    cron_pattern: Optional[str] = None
) -> Reminder:
    """
    Create a new reminder in the database.
    """
    db_reminder = Reminder(
        user_phone=user_phone,
        message_content=message_content,
        trigger_time=trigger_time,
        is_recurring=is_recurring,
        cron_pattern=cron_pattern,
        status=ReminderStatus.PENDING
    )
    db.add(db_reminder)
    await db.commit()
    await db.refresh(db_reminder)
    return db_reminder

async def get_reminder(db: AsyncSession, reminder_id: int) -> Optional[Reminder]:
    """
    Get a reminder by its ID.
    """
    result = await db.execute(select(Reminder).where(Reminder.id == reminder_id))
    return result.scalars().first()

async def get_user_reminders(
    db: AsyncSession, 
    user_phone: str, 
    status: Optional[ReminderStatus] = None
) -> List[Reminder]:
    """
    Get all reminders for a specific user, optionally filtered by status.
    """
    query = select(Reminder).where(Reminder.user_phone == user_phone)
    if status:
        query = query.where(Reminder.status == status)
    result = await db.execute(query)
    return list(result.scalars().all())

async def update_reminder_status(
    db: AsyncSession, reminder_id: int, status: ReminderStatus
) -> Optional[Reminder]:
    """
    Update the status of a reminder.
    """
    reminder = await get_reminder(db, reminder_id)
    if reminder:
        reminder.status = status
        await db.commit()
        await db.refresh(reminder)
    return reminder

async def delete_reminder(db: AsyncSession, reminder_id: int) -> bool:
    """
    Delete a reminder by ID.
    """
    reminder = await get_reminder(db, reminder_id)
    if reminder:
        await db.delete(reminder)
        await db.commit()
        return True
    return False
