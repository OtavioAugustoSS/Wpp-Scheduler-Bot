from app.core.config import settings

async def send_whatsapp_message(to: str, message: str):
    """
    Mock function to send WhatsApp message.
    In production, this would call Keybe / Meta API.
    """
    print(f"--- WHATSAPP MOCK ---")
    print(f"TO: {to}")
    print(f"MESSAGE: {message}")
    print(f"---------------------")
    return True
