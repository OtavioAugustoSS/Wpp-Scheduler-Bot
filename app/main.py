from fastapi import FastAPI
from app.core.config import settings

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

@app.get("/")
async def root():
    return {"message": "Wpp-Scheduler-Bot is running"}

@app.on_event("startup")
async def startup_event():
    from app.core.database import engine, Base
    from app.models.reminder import Reminder  # Import models to register them
    from app.services.scheduler import start_scheduler
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Start Scheduler
    start_scheduler()

from app.routers import webhook
app.include_router(webhook.router)
