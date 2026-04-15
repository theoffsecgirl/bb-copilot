from cli.vault import load_system_prompt, load_all
from cli.llm import ask
from cli.models import CopilotResponse
from pathlib import Path


REPORT_SYSTEM = """
You are an expert bug bounty report writer. Given a finding description, generate a complete, professional bug bounty report ready to submit to HackerOne, Bugcrowd or YesWeHack.

The report MUST follow this exact structure:

## Título
[Título conciso y específico: Vuln + Endpoint + Impacto]

## Resumen
[2-3 frases: qué es, dónde está, impacto real. Sin palabrería.]

## Severidad
[Critical / High / Medium / Low / Informational]
Justificación CVSS: [vector y puntuación si aplica]

## Descripción técnica
[Explicación técnica precisa de la vulnerabilidad y por qué existe]

## Pasos para reproducir
1. ...
2. ...
3. ...
[Cada paso debe ser reproducible sin contexto adicional]

## Prueba de concepto
```http
[Request/response completo o payload]
```

## Impacto
[Impacto concreto: qué datos, qué acciones, qué usuarios afectados, escala posible]

## Recomendación de fix
[Fix técnico concreto, no genérico]

Reglas:
- Sé directo y técnico.
- El impacto debe ser real, no teórico.
- Los steps deben ser reproducibles por un triager sin acceso a tu sesión.
- Responde en el mismo idioma que el input.
"""


def run_report(
    finding: str,
    context_file: str | None = None,
    target: str | None = None,
) -> CopilotResponse:
    """Genera un borrador de reporte completo listo para enviar."""
    vault = load_all()

    extra = ""
    if context_file:
        p = Path(context_file)
        if p.exists():
            extra += f"\n\nContexto adicional del fichero:\n{p.read_text()}"
    if target:
        extra += f"\n\nTarget: {target}"

    user_msg = (
        f"Genera un reporte de bug bounty completo para el siguiente hallazgo:\n\n"
        f"{finding}"
        f"{extra}\n\n"
        f"Incluye requests reales si los hay en el contexto. "
        f"El reporte debe estar listo para enviar."
    )
    return ask(REPORT_SYSTEM, user_msg, vault.content)
