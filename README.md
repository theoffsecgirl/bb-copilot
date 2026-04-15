# bb-copilot

> AI-powered bug bounty assistant. Methodology vault + CLI guided by real hunter knowledge.

```
bbcopilot ask "api.target.com uses JWT and org_id in every request"
bbcopilot plan --target api.target.com --type api
bbcopilot vuln idor --context notes.txt
bbcopilot triage --finding "IDOR on /api/v1/invoices/{id}"
```

## What it does

- Reads your local vault (Markdown playbooks by vuln type and phase)
- Sends the right context + your input to GPT-4o
- Returns structured, actionable output: hypothesis → steps → evidence → impact
- Does NOT automate attacks. It guides your thinking.

## Stack

- Python 3.12+
- [Typer](https://typer.tiangolo.com/) + [Rich](https://github.com/Textualize/rich)
- OpenAI API (`gpt-4o`)
- Markdown vault (local, version-controlled)

## Install

```bash
git clone https://github.com/theoffsecgirl/bb-copilot
cd bb-copilot
pip install -e .
cp .env.example .env
# Add your OPENAI_API_KEY to .env
```

## Usage

```bash
# Ask anything with your vault as context
bbcopilot ask "target has GraphQL endpoint with user_id in mutations"

# Get a prioritized attack plan for a target
bbcopilot plan --target example.com --type web
bbcopilot plan --target api.example.com --type api

# Get a specific vuln playbook + guidance
bbcopilot vuln ssrf
bbcopilot vuln idor --context my-notes.txt

# Triage a finding and get next steps
bbcopilot triage --finding "open redirect on /redirect?url="
```

## Vault structure

```
vault/
├── methodology/    # Recon, triage, JS analysis, API hunting, reporting
├── vulns/          # Playbook per vulnerability class
├── patterns/       # Auth bypass, multi-tenant, role confusion
└── prompts/        # System prompt and model rules
```

## Modes

| Command | Input | Output |
|---|---|---|  
| `ask` | Free text observation | Prioritized hypothesis + steps |
| `plan` | Target + type | Full attack plan |
| `vuln` | Vuln class + optional context | Playbook + what to probe |
| `triage` | Finding description | Impact + evidence needed + report structure |

## Philosophy

- Output over explanation
- Structured always: hypothesis → checks → evidence → impact
- Vault is the brain. Model is the engine.
- No black boxes. You own the knowledge.

---

By [@theoffsecgirl](https://github.com/theoffsecgirl)
