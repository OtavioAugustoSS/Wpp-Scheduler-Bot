import json
from typing import Dict, Any
from openai import AsyncOpenAI
from app.core.config import settings

client = AsyncOpenAI(
    api_key=settings.NVIDIA_API_KEY,
    base_url=settings.OPENAI_BASE_URL
)

# Using Llama 3.1 70B Instruct as requested
MODEL_NAME = "meta/llama-3.1-70b-instruct"

SYSTEM_PROMPT = """
You are a smart personal assistant for WhatsApp.
Your job is to extract scheduling intentions from the user's message.
You must output ONLY valid JSON. No markdown, no explanations.

The JSON structure must be:
{
  "action": "schedule_once" | "schedule_recurring" | "chat",
  "datetime_iso": "YYYY-MM-DDTHH:MM:SS" (only for schedule_once, otherwise null),
  "cron_pattern": "cron string" (only for schedule_recurring, e.g., "0 8 * * *", otherwise null),
  "reminder_text": "text content of the reminder",
  "response_message": "A natural language response to the user confirming the action or answering the chat"
}

Rules:
1. If the user wants a one-time reminder (e.g. "Remind me to drink water in 2 hours"), set action to "schedule_once", calculate the future time based on the current time provided in context, and put it in "datetime_iso".
2. If the user wants a recurring reminder (e.g. "Remind me every day at 8am"), set action to "schedule_recurring" and generate a standard cron expression in "cron_pattern".
3. If the user is just chatting or asking a question, set action to "chat" and provide a helpful answer in "response_message".
4. "reminder_text" should be the core message (e.g., "Drink water").
5. ALWAYS return the fields, use null if not applicable.
"""

async def process_user_message(user_text: str, current_time_iso: str) -> Dict[str, Any]:
    """
    Process user text using NVIDIA NIM LLM to determine intent and extract data.
    """
    try:
        response = await client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": f"Current time: {current_time_iso}\n{SYSTEM_PROMPT}"},
                {"role": "user", "content": user_text}
            ],
            temperature=0.2, # Low temperature for more deterministic JSON
            max_tokens=1024,
            stream=False
        )

        content = response.choices[0].message.content.strip()
        
        # Attempt to clean up if the model adds markdown code blocks
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
            
        result = json.loads(content.strip())
        return result

    except json.JSONDecodeError:
        # Fallback if raw text is returned
        return {
            "action": "chat",
            "datetime_iso": None,
            "cron_pattern": None,
            "reminder_text": None,
            "response_message": "Sorry, I couldn't process that request clearly. Could you try again?"
        }
    except Exception as e:
        # Log error in production
        print(f"Error calling LLM: {e}")
        return {
            "action": "chat",
            "datetime_iso": None,
            "cron_pattern": None,
            "reminder_text": None,
            "response_message": "I'm having trouble connecting to my brain right now. Please try again later."
        }
