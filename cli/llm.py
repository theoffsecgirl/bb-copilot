import os
from openai import OpenAI
from dotenv import load_dotenv
from cli.models import CopilotResponse

load_dotenv()

# Soporta cualquier proveedor compatible con la API de OpenAI:
# Groq, Ollama, OpenAI, Together, Anyscale, etc.
# Solo cambia OPENAI_API_KEY, OPENAI_BASE_URL y OPENAI_MODEL en .env

_api_key = os.getenv("OPENAI_API_KEY", "")
_base_url = os.getenv("OPENAI_BASE_URL")  # None = OpenAI por defecto

client = OpenAI(
    api_key=_api_key,
    base_url=_base_url,  # None usa https://api.openai.com/v1
)

MODEL = os.getenv("OPENAI_MODEL", "llama-3.3-70b-versatile")
MAX_TOKENS = int(os.getenv("BBCOPILOT_MAX_TOKENS", "2048"))
TEMPERATURE = float(os.getenv("BBCOPILOT_TEMPERATURE", "0.2"))


def ask(system_prompt: str, user_message: str, context: str = "") -> CopilotResponse:
    """Envia un mensaje al LLM con el vault como contexto inyectado."""
    full_system = system_prompt
    if context:
        full_system += f"\n\n# Vault Context\n{context}"

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": full_system},
            {"role": "user", "content": user_message},
        ],
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE,
    )

    return CopilotResponse(
        raw=response.choices[0].message.content or "",
        tokens_used=response.usage.total_tokens if response.usage else 0,
    )
