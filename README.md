# bb-copilot

> Asistente de bug bounty con IA. Vault de metodología + CLI guiado por conocimiento real de hunter.

```
bbcopilot ask "api.target.com usa JWT y org_id en cada request"
bbcopilot plan --target api.target.com --type api
bbcopilot vuln idor --context notas.txt
bbcopilot triage --finding "IDOR en /api/v1/invoices/{id}"
```

## Qué hace

- Lee tu vault local (playbooks en Markdown por tipo de vuln y fase)
- Envía el contexto adecuado + tu input a GPT-4o
- Devuelve output estructurado y accionable: hipótesis → pasos → evidencia → impacto
- NO automatiza ataques. Guía tu razonamiento.

## Stack

- Python 3.12+
- [Typer](https://typer.tiangolo.com/) + [Rich](https://github.com/Textualize/rich)
- OpenAI API (`gpt-4o`)
- Vault en Markdown (local, versionado en Git)

## Instalación

```bash
git clone https://github.com/theoffsecgirl/bb-copilot
cd bb-copilot
pip install -e .
cp .env.example .env
# Añadir OPENAI_API_KEY en .env
```

## Uso

```bash
# Pregunta libre con todo el vault como contexto
bbcopilot ask "el target tiene GraphQL con user_id en las mutations"

# Plan de ataque priorizado para un target
bbcopilot plan --target example.com --type web
bbcopilot plan --target api.example.com --type api

# Playbook de una vulnerabilidad concreta
bbcopilot vuln ssrf
bbcopilot vuln idor --context mis-notas.txt

# Triage de un hallazgo con siguientes pasos
bbcopilot triage --finding "open redirect en /redirect?url="

# Listar todos los playbooks disponibles en el vault
bbcopilot vault-list
```

## Estructura del vault

```
vault/
├── methodology/    # Recon, triage de activos, análisis JS, API hunting, reporting
├── vulns/          # Playbook por clase de vulnerabilidad
├── patterns/       # Auth bypass, multi-tenant, role confusion, race conditions
└── prompts/        # System prompt y reglas del modelo
```

## Comandos

| Comando | Input | Output |
|---|---|---|
| `ask` | Observación en texto libre | Hipótesis priorizada + pasos |
| `plan` | Target + tipo | Plan de ataque completo |
| `vuln` | Clase de vuln + contexto opcional | Playbook + qué probar |
| `triage` | Descripción del hallazgo | Impacto + evidencia necesaria + estructura de reporte |
| `vault-list` | — | Lista de playbooks disponibles |

## Vulnerabilidades cubiertas

`IDOR` · `SSRF` · `XSS` · `SQLi` · `Open Redirect` · `File Upload` · `Subdomain Takeover` · `Business Logic` · `CORS` · `XXE` · `SSTI` · `OAuth`

## Filosofía

- Resultado sobre explicación
- Siempre estructurado: hipótesis → checks → evidencia → impacto
- El vault es el cerebro. El modelo es el motor.
- Sin cajas negras. El conocimiento es tuyo.

---

By [@theoffsecgirl](https://github.com/theoffsecgirl)
