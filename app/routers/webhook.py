from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from app.core.config import settings
from app.services.ai_service import process_user_message
from app.services.whatsapp import send_whatsapp_message
from app.core.database import AsyncSessionLocal
from app.services.reminder_crud import create_reminder
from datetime import datetime

router = APIRouter()

@router.get("/webhook")
async def verify_webhook(request: Request):
    """
    Verification endpoint for WhatsApp Webhook.
    """
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
    Logic to process the message with AI and take action.
    """
    now_iso = datetime.now().isoformat()
    ai_result = await process_user_message(text, now_iso)
    
    print(f"AI Result: {ai_result}")

    action = ai_result.get("action")
    response_text = ai_result.get("response_message", "Entendido.")

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
        
        # Override response for scheduling confirmation if needed, or use AI's
        if not response_text:
            response_text = "Lembrete agendado com sucesso!"

    # Send response back to user
    await send_whatsapp_message(phone, response_text)
