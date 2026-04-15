import os
from openai import OpenAI
from dotenv import load_dotenv
from cli.models import CopilotResponse

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
MAX_TOKENS = int(os.getenv("BBCOPILOT_MAX_TOKENS", "2048"))
TEMPERATURE = float(os.getenv("BBCOPILOT_TEMPERATURE", "0.2"))


def ask(system_prompt: str, user_message: str, context: str = "") -> CopilotResponse:
    """Send a message to the LLM with vault context injected."""
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
