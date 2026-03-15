from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from app.core.config import settings
from app.services.ai_service import process_user_message
from app.services.whatsapp import send_whatsapp_message
from app.core.database import AsyncSessionLocal
from app.services.reminder_crud import create_reminder, get_user_reminders
from app.models.reminder import ReminderStatus
from datetime import datetime

router = APIRouter()

# Simple in-memory session history: {phone_number: [{"role": "...", "content": "..."}, ...]}
# In a real app, you might want to back this by Redis or the database.
SESSION_HISTORY = {}
MAX_HISTORY_LENGTH = 10 # Keep the last 10 messages

@router.get("/webhook")
async def verify_webhook(request: Request):
# ... (keep existing verify_webhook) ...
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == settings.WHATSAPP_VERIFY_TOKEN:
            print("Webhook verified!")
            return int(challenge)
        else:
            raise HTTPException(status_code=403, detail="Verification failed")
    
    return {"status": "ok"}

@router.post("/webhook")
async def handle_message(request: Request, background_tasks: BackgroundTasks):
    """
    Handle incoming WhatsApp messages.
    """
    try:
        data = await request.json()
        entry = data.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])

        if not messages:
            return {"status": "no message"}

        message = messages[0]
        from_phone = message.get("from")
        text_body = message.get("text", {}).get("body")

        if not from_phone or not text_body:
            return {"status": "invalid message format"}

        # Process message in background to avoid timeout
        background_tasks.add_task(process_incoming_message, from_phone, text_body)

        return {"status": "received"}
    except Exception as e:
        print(f"Error processing webhook: {e}")
        return {"status": "error"}

async def process_incoming_message(phone: str, text: str):
    """
    Logic to process the message with AI, acting on memory, context, and intent.
    """
    now_iso = datetime.now().isoformat()
    
    # 1. Fetch Database Context (Active Reminders)
    reminders_context_str = "Nenhum lembrete no momento."
    async with AsyncSessionLocal() as db:
        active_reminders = await get_user_reminders(db, phone, status=ReminderStatus.PENDING)
        if active_reminders:
            context_lines = []
            for r in active_reminders:
                if r.is_recurring:
                    context_lines.append(f"- RECORRENTE ({r.cron_pattern}): {r.message_content} (ID: {r.id})")
                elif r.trigger_time:
                    context_lines.append(f"- ÚNICO ({r.trigger_time.isoformat()}): {r.message_content} (ID: {r.id})")
            if context_lines:
                reminders_context_str = "\n".join(context_lines)

    # 2. Fetch Short-Term Chat History
    user_history = SESSION_HISTORY.get(phone, [])

    # 3. Call AI Service
    ai_result = await process_user_message(
        user_text=text, 
        current_time_iso=now_iso, 
        reminders_context=reminders_context_str,
        chat_history=user_history
    )
    
    print(f"AI Result: {ai_result}")

    action = ai_result.get("action")
    response_text = ai_result.get("response_message", "Entendido.")

    # 4. Handle Actions
    if action in ["schedule_once", "schedule_recurring"]:
        # Save to DB
        async with AsyncSessionLocal() as db:
            trigger_time = None
            if ai_result.get("datetime_iso"):
                 try:
                    trigger_time = datetime.fromisoformat(ai_result.get("datetime_iso"))
                 except ValueError:
                    print("Invalid datetime format from AI")
            
            await create_reminder(
                db=db,
                user_phone=phone,
                message_content=ai_result.get("reminder_text", text),
                trigger_time=trigger_time,
                is_recurring=(action == "schedule_recurring"),
                cron_pattern=ai_result.get("cron_pattern")
            )
        
        if not response_text:
            response_text = "Lembrete agendado com sucesso!"

    elif action == "list_reminders":
        # Override the response with the formatted list of reminders
        if active_reminders:
            response_text += "\n\n" + reminders_context_str
        else:
            response_text = "Você não tem nenhum lembrete agendado no momento."

    # 5. Send response back to user
    await send_whatsapp_message(phone, response_text)

    # 6. Update Session History
    user_history.append({"role": "user", "content": text})
    user_history.append({"role": "assistant", "content": response_text})
    
    # Keep only the last N messages
    if len(user_history) > MAX_HISTORY_LENGTH * 2:
        user_history = user_history[-(MAX_HISTORY_LENGTH * 2):]
        
    SESSION_HISTORY[phone] = user_history
