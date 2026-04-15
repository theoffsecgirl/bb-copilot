# bb-copilot

> AI-powered bug bounty assistant. Methodology vault + CLI guided by real hunter knowledge.

> 🇪🇸 [Versión en español](README.es.md)

```
bbcopilot ask "api.target.com uses JWT and org_id in every request"
bbcopilot plan --target api.target.com --type api
bbcopilot vuln idor --context notes.txt
bbcopilot triage --finding "IDOR on /api/v1/invoices/{id}"
bbcopilot report --finding "IDOR on /api/v1/invoices/{id}" --target api.target.com -o report.md
```

## What it does

- Reads your local vault (Markdown playbooks by vuln type and phase)
- Sends the right context + your input to the configured model
- Returns structured, actionable output: hypotheses → steps → evidence → impact
- Generates complete reports ready to submit to HackerOne, Bugcrowd or YesWeHack
- Saves local history of all sessions in `~/.bbcopilot/history/`
- Does NOT automate attacks. Guides your reasoning.

## Stack

- Python 3.12+
- [Typer](https://typer.tiangolo.com/) + [Rich](https://github.com/Textualize/rich)
- Any OpenAI-compatible LLM API: **Ollama, Groq, OpenAI, Anthropic**
- Markdown vault (local, Git-versioned)
- Local JSON history (`~/.bbcopilot/history/`)

## Installation

```bash
git clone https://github.com/theoffsecgirl/bb-copilot
cd bb-copilot
make setup
```

Then edit `.env` according to your chosen provider (see **LLM Providers** section).

## LLM Providers

| Provider | Cost | Privacy | Setup |
|---|---|---|---|
| **Ollama** (default) | Free | Local — 100% private | `brew install ollama` |
| Groq | Free (limited tier) | Cloud | API key at console.groq.com |
| OpenAI | Paid | Cloud | API key at platform.openai.com |
| Anthropic | Paid | Cloud | API key at console.anthropic.com |

### Ollama (default)

```bash
brew install ollama
ollama pull llama3.1   # ~4GB, one-time
ollama serve           # run in background
```

`.env`:
```bash
OPENAI_API_KEY=ollama
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_MODEL=llama3.1
```

### Groq (free, cloud)

Note: free tier has ~6000 token context limit. Add to `.env`:
```bash
BBCOPILOT_MAX_CONTEXT_TOKENS=5000
```

### OpenAI

```bash
OPENAI_API_KEY=sk-proj-...
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o
```

## Usage

```bash
# Free-form question with full vault as context
bbcopilot ask "target has GraphQL with user_id in mutations"

# Prioritized attack plan for a target
bbcopilot plan --target example.com --type web
bbcopilot plan --target api.example.com --type api

# Playbook for a specific vulnerability
bbcopilot vuln ssrf
bbcopilot vuln idor --context my-notes.txt

# Triage a finding with next steps
bbcopilot triage --finding "open redirect on /redirect?url="

# Generate complete report ready to submit
bbcopilot report --finding "IDOR on /api/v1/invoices/{id} exposes other users' invoices"
bbcopilot report --finding "..." --target api.example.com --context requests.txt --output report.md

# Session history
bbcopilot history
bbcopilot history --last 5
bbcopilot history --clear

# List all available playbooks
bbcopilot vault-list
```

## Commands

| Command | Input | Output |
|---|---|---|
| `ask` | Free-form observation | Prioritized hypotheses + steps |
| `plan` | Target + type | Full attack plan |
| `vuln` | Vuln class + optional context | Playbook + what to test |
| `triage` | Finding description | Severity + evidence + next steps |
| `report` | Finding + optional context | Full report (Markdown) |
| `history` | — | Last sessions in table |
| `vault-list` | — | List of available playbooks |

## Vault structure

```
vault/
├── methodology/    # Recon, asset triage, JS analysis, API hunting, reporting
├── vulns/          # Playbook per vulnerability class
├── patterns/       # Auth bypass, multi-tenant, role confusion, race conditions
└── prompts/        # System prompt and model rules
```

## Covered vulnerabilities

`IDOR` · `SSRF` · `XSS` · `SQLi` · `Open Redirect` · `File Upload` · `Subdomain Takeover` · `Business Logic` · `CORS` · `XXE` · `SSTI` · `OAuth`

## Makefile

```bash
make setup    # Full initial setup
make install  # Dependencies only
make dev      # Dependencies + dev (pytest, ruff)
make test     # Run tests
make lint     # Linter
make format   # Format code
make vault    # List vault
make ask Q="your question"  # Quick query
make clean    # Clean caches
```

## History

All sessions are automatically saved to `~/.bbcopilot/history/` in JSON format.
Disable with `--no-save` on any command.

## Philosophy

- Result over explanation
- Always structured: hypotheses → checks → evidence → impact
- The vault is the brain. The model is the engine.
- No black boxes. The knowledge is yours.

---

By [@theoffsecgirl](https://github.com/theoffsecgirl)
