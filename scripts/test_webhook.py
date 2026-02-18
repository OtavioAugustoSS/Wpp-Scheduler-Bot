import requests
import json
import sys

# URL of your local FastAPI webhook
WEBHOOK_URL = "http://localhost:8000/webhook"

def send_test_message(text_content):
    """
    Simulate a WhatsApp message event sent to the webhook.
    """
    payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "1234567890",
                                "phone_number_id": "PHONE_NUMBER_ID"
                            },
                            "contacts": [
                                {
                                    "profile": {
                                        "name": "Test User"
                                    },
                                    "wa_id": "5511999999999"
                                }
                            ],
                            "messages": [
                                {
                                    "from": "5511999999999",
                                    "id": "wamid.HBgLMT...",
                                    "timestamp": "1700000000",
                                    "text": {
                                        "body": text_content
                                    },
                                    "type": "text"
                                }
                            ]
                        },
                        "field": "messages"
                    }
                ]
            }
        ]
    }

    try:
        print(f"Sending message: '{text_content}' to {WEBHOOK_URL}...")
        response = requests.post(WEBHOOK_URL, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to localhost:8000. Is the server running?")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        message = " ".join(sys.argv[1:])
    else:
        print("Usage: python scripts/test_webhook.py <message>")
        print("Example: python scripts/test_webhook.py Me lembre de tomar remedio em 1 minuto")
        # Default test message
        message = "Me lembre de testar o bot em 1 minuto"
    
    send_test_message(message)
