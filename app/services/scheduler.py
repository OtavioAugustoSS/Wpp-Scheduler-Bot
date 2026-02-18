import asyncio
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.reminder import Reminder, ReminderStatus
from app.services.whatsapp import send_whatsapp_message
from app.services.reminder_crud import update_reminder_status

scheduler = AsyncIOScheduler()

async def check_reminders():
    """
    Periodic job to check for due reminders.
    """
    print("Checking for reminders...")
    async with AsyncSessionLocal() as db:
        now = datetime.now()
        
        # 1. Fetch pending one-time reminders that are due
        query = select(Reminder).where(
            Reminder.status == ReminderStatus.PENDING,
            Reminder.trigger_time <= now,
            Reminder.is_recurring == False
        )
        result = await db.execute(query)
        due_reminders = result.scalars().all()

        for reminder in due_reminders:
            print(f"Sending reminder {reminder.id} to {reminder.user_phone}")
            await send_whatsapp_message(reminder.user_phone, reminder.message_content)
            await update_reminder_status(db, reminder.id, ReminderStatus.SENT)
            
        # TODO: Implement recurring logic logic here (checking cron patterns)
        # For now, we only handle simple one-time reminders.

def start_scheduler():
    """
    Start the APScheduler.
    """
    scheduler.add_job(check_reminders, 'interval', seconds=60)
    scheduler.start()
    print("Scheduler started.")
