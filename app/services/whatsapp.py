import httpx
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

async def send_whatsapp_message(to: str, message: str):
    """
    Envia mensagem real usando a API do WhatsApp Cloud (Meta).
    """
    if not settings.WHATSAPP_API_TOKEN or "placeholder" in settings.WHATSAPP_API_TOKEN:
        print(f"--- WHATSAPP MOCK (Falta Token Real) ---")
        print(f"TO: {to}")
        print(f"MESSAGE: {message}")
        print(f"----------------------------------------")
        return True

    # A API do WhatsApp exige que o número não tenha o '+'
    # E para testes no modo Sandbox, você só pode enviar para números verificados
    
    url = f"https://graph.facebook.com/v17.0/{settings.WHATSAPP_PHONE_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_API_TOKEN}",
        "Content-Type": "application/json",
    }
    
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message},
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=data)
            response.raise_for_status()
            logger.info(f"Mensagem enviada para {to}: {response.status_code}")
            return True
        except httpx.HTTPStatusError as e:
            logger.error(f"Erro no envio WhatsApp: {e.response.text}")
            return False
        except Exception as e:
            logger.error(f"Falha na conexão com WhatsApp: {e}")
            return False