# bb-copilot

> Asistente de bug bounty con IA. Vault de metodología + CLI guiado por conocimiento real de hunter.

```
bbcopilot ask "api.target.com usa JWT y org_id en cada request"
bbcopilot plan --target api.target.com --type api
bbcopilot vuln idor --context notas.txt
bbcopilot triage --finding "IDOR en /api/v1/invoices/{id}"
bbcopilot report --finding "IDOR en /api/v1/invoices/{id}" --target api.target.com -o reporte.md
```

## Qué hace

- Lee tu vault local (playbooks en Markdown por tipo de vuln y fase)
- Envía el contexto adecuado + tu input al modelo configurado
- Devuelve output estructurado y accionable: hipótesis → pasos → evidencia → impacto
- Genera reportes completos listos para enviar a HackerOne, Bugcrowd o YesWeHack
- Guarda historial local de todas las sesiones en `~/.bbcopilot/history/`
- NO automatiza ataques. Guía tu razonamiento.

## Stack

- Python 3.12+
- [Typer](https://typer.tiangolo.com/) + [Rich](https://github.com/Textualize/rich)
- Cualquier LLM compatible con API OpenAI: **Ollama, Groq, OpenAI, Anthropic**
- Vault en Markdown (local, versionado en Git)
- Historial en JSON local (`~/.bbcopilot/history/`)

## Instalación

```bash
git clone https://github.com/theoffsecgirl/bb-copilot
cd bb-copilot
make setup
```

Luego edita `.env` según tu proveedor elegido (ver sección **Proveedores LLM**).

## Proveedores LLM

| Proveedor | Coste | Privacidad | Setup |
|---|---|---|---|
| **Ollama** (por defecto) | Gratis | Local — 100% privado | `brew install ollama` |
| Groq | Gratis (tier limitado) | Nube | API key en console.groq.com |
| OpenAI | De pago | Nube | API key en platform.openai.com |
| Anthropic | De pago | Nube | API key en console.anthropic.com |

### Ollama (por defecto)

```bash
brew install ollama
ollama pull llama3.1   # ~4GB, solo una vez
ollama serve           # arrancar en background
```

`.env`:
```bash
OPENAI_API_KEY=ollama
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_MODEL=llama3.1
```

### Groq (gratis, nube)

Atención: el tier gratuito tiene límite de ~6000 tokens de contexto. Añade esto al `.env`:
```bash
BBCOPILOT_MAX_CONTEXT_TOKENS=5000
```

### OpenAI

```bash
OPENAI_API_KEY=sk-proj-...
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o
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

# Generar reporte completo listo para enviar
bbcopilot report --finding "IDOR en /api/v1/invoices/{id} permite leer facturas ajenas"
bbcopilot report --finding "..." --target api.example.com --context requests.txt --output reporte.md

# Historial de sesiones
bbcopilot history
bbcopilot history --last 5
bbcopilot history --clear

# Listar todos los playbooks disponibles
bbcopilot vault-list
```

## Comandos

| Comando | Input | Output |
|---|---|---|
| `ask` | Observación en texto libre | Hipótesis priorizada + pasos |
| `plan` | Target + tipo | Plan de ataque completo |
| `vuln` | Clase de vuln + contexto opcional | Playbook + qué probar |
| `triage` | Descripción del hallazgo | Severidad + evidencia + siguientes pasos |
| `report` | Hallazgo + contexto opcional | Reporte completo (Markdown) |
| `history` | — | Últimas sesiones en tabla |
| `vault-list` | — | Lista de playbooks disponibles |

## Estructura del vault

```
vault/
├── methodology/    # Recon, triage de activos, análisis JS, API hunting, reporting
├── vulns/          # Playbook por clase de vulnerabilidad
├── patterns/       # Auth bypass, multi-tenant, role confusion, race conditions
└── prompts/        # System prompt y reglas del modelo
```

## Vulnerabilidades cubiertas

`IDOR` · `SSRF` · `XSS` · `SQLi` · `Open Redirect` · `File Upload` · `Subdomain Takeover` · `Business Logic` · `CORS` · `XXE` · `SSTI` · `OAuth`

## Makefile

```bash
make setup    # Instalación inicial completa
make install  # Solo dependencias
make dev      # Dependencias + dev (pytest, ruff)
make test     # Ejecutar tests
make lint     # Linter
make format   # Formatear código
make vault    # Listar vault
make ask Q="tu pregunta"  # Consulta rápida
make clean    # Limpiar cachés
```

## Historial

Todas las sesiones se guardan automáticamente en `~/.bbcopilot/history/` en formato JSON.
Desactívalo con `--no-save` en cualquier comando.

## Filosofía

- Resultado sobre explicación
- Siempre estructurado: hipótesis → checks → evidencia → impacto
- El vault es el cerebro. El modelo es el motor.
- Sin cajas negras. El conocimiento es tuyo.

---

By [@theoffsecgirl](https://github.com/theoffsecgirl)
