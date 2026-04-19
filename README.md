<div align="center">

# bb-copilot

**AI-powered bug bounty assistant — methodology vault + guided CLI**

![Language](https://img.shields.io/badge/Python-3.12+-9E4AFF?style=flat-square&logo=python&logoColor=white)
![Version](https://img.shields.io/badge/version-0.1.0-9E4AFF?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-9E4AFF?style=flat-square)
![LLM](https://img.shields.io/badge/LLM-Ollama%20%7C%20Groq%20%7C%20OpenAI%20%7C%20Anthropic-111111?style=flat-square)
![Category](https://img.shields.io/badge/Category-Bug%20Bounty%20%7C%20AI%20Tooling-111111?style=flat-square)

*by [theoffsecgirl](https://github.com/theoffsecgirl)*

> 🇪🇸 [Versión en español](README.es.md)

</div>

---

> AI-powered bug bounty assistant. Methodology vault + classic guided CLI + findings workflow for real bug bounty pipelines.

```bash
bbcopilot ask "api.target.com uses JWT and org_id in every request"
bbcopilot plan --target api.target.com --type api
bbcopilot vuln idor --context notes.txt
bbcopilot triage --finding "IDOR on /api/v1/invoices/{id}"
bbcopilot ingest webxray out.jsonl
bbcopilot correlate
bbcopilot auto-triage
bbcopilot exploit-plan
```

## What it does

- Reads your local vault (Markdown playbooks by vuln type and phase)
- Sends the right context + your input to the configured model
- Returns structured, actionable output: hypotheses → steps → evidence → impact
- Generates complete reports ready to submit to HackerOne, Bugcrowd or YesWeHack
- Saves local history of all sessions in `~/.bbcopilot/history/`
- Stores normalized findings in `~/.bbcopilot/findings/`
- Correlates findings from external tools to prioritize hotter surfaces
- Does NOT automate attacks. Guides your reasoning.

## Stack

- Python 3.12+
- [Typer](https://typer.tiangolo.com/) + [Rich](https://github.com/Textualize/rich)
- Any OpenAI-compatible LLM API: **Ollama, Groq, OpenAI, Anthropic**
- Markdown vault (local, Git-versioned)
- Local JSON history (`~/.bbcopilot/history/`)
- Local JSONL findings store (`~/.bbcopilot/findings/`)

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

## Findings workflow

This layer turns `bb-copilot` from a guided assistant into a workflow hub:

```bash
# 1. Ingest output from external tools
bbcopilot ingest webxray out.jsonl

# 2. Review stored findings
bbcopilot findings
bbcopilot findings --tool webxray --vector xss --host api.example.com

# 3. Correlate by host/vector
bbcopilot correlate

# 4. Triage the hottest cluster automatically
bbcopilot auto-triage

# 5. Generate an exploit validation plan
bbcopilot exploit-plan

# 6. Generate a report from one finding or top cluster
bbcopilot report-id --id F-202604190001-0001
bbcopilot report-top -o top-report.md
```

### Example integration

```bash
webxray -u https://target.com --format jsonl --json-output out.jsonl
bbcopilot ingest webxray out.jsonl
bbcopilot correlate
bbcopilot auto-triage
bbcopilot exploit-plan
```

---

## Commands

| Command | Input | Output |
|---|---|---|
| `ask` | Free-form observation | Prioritized hypotheses + steps |
| `plan` | Target + type | Full attack plan |
| `vuln` | Vuln class + optional context | Playbook + what to test |
| `triage` | Finding description | Severity + evidence + next steps |
| `triage-id` | Stored finding ID | Triage from normalized finding |
| `report` | Finding + optional context | Full report (Markdown) |
| `report-id` | Stored finding ID | Full report from one finding |
| `report-top` | — | Full report from top correlation |
| `ingest` | Tool name + JSON/JSONL | Normalize and persist findings |
| `findings` | Optional filters | List stored findings |
| `correlate` | — | Group findings by host/vector |
| `auto-triage` | — | Triage top correlation |
| `exploit-plan` | — | Exploit/validation plan for top correlation |
| `history` | — | Last sessions in table |
| `vault-list` | — | List of available playbooks |

## Vault structure

```text
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

## Storage

- History: `~/.bbcopilot/history/`
- Findings: `~/.bbcopilot/findings/`

## Philosophy

- Result over explanation
- Always structured: hypotheses → checks → evidence → impact
- The vault is the brain. The model is the engine.
- Findings make the workflow reproducible.
- No black boxes. The knowledge is yours.

---

By [@theoffsecgirl](https://github.com/theoffsecgirl)
