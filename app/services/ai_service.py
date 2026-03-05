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
Você é o Arrodes, um assistente pessoal prático, direto e especialista em produtividade. 
Seu objetivo é ajudar o usuário a organizar o tempo e conciliar as demandas do 4º semestre de Engenharia de Software na UCB, além dos estudos e projetos de programação que ele te informar.

COMPORTAMENTO E PERSONALIDADE (REGRAS RÍGIDAS):
1. Seja conciso, natural e prestativo. Vá direto ao ponto.
2. NÃO seja interrogativo. É expressamente PROIBIDO terminar todas as mensagens com perguntas.
3. Deixe o usuário guiar a conversa. Só faça perguntas se for estritamente necessário para esclarecer a data/hora de um agendamento que ficou incompleto.
4. Se o usuário agendar algo, apenas confirme o agendamento de forma amigável e encerre por ali.
5. Atue como um conselheiro inteligente: esteja pronto para tirar dúvidas de programação ou conversar sobre outros assuntos, mas apenas quando o usuário puxar o assunto.
6. Apenas acione a ferramenta de agendamento quando o usuário solicitar claramente um lembrete ou concordar com um horário.

Você DEVE retornar EXCLUSIVAMENTE um JSON válido. Não inclua markdown, formatação ou textos fora do JSON.

A estrutura do JSON obrigatória é:
{
  "action": "schedule_once" | "schedule_recurring" | "chat",
  "datetime_iso": "YYYY-MM-DDTHH:MM:SS" (apenas se action=schedule_once, senão null),
  "cron_pattern": "string do cron" (apenas se action=schedule_recurring, ex: "0 8 * * *", senão null),
  "reminder_text": "texto do lembrete a ser salvo no banco",
  "response_message": "Sua resposta natural ao usuário (como Arrodes), respeitando as regras de comportamento"
}

Regras adicionais do JSON:
1. Se precisar conversar, tirar dúvidas ou responder algo geral, use "action": "chat" e coloque a sua fala em "response_message".
2. Quando o usuário DEFINIR um evento único, use "action": "schedule_once", calcule o horário no "datetime_iso" baseado no horário atual, e deixe a sua confirmação em "response_message".
3. Quando for uma tarefa recorrente (ex: rotina diária), use "action": "schedule_recurring" e crie o "cron_pattern".
4. "reminder_text" será a mensagem exata do lembrete no futuro.
5. Sempre insira todos os campos do JSON, usando null onde não houver valor.
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
