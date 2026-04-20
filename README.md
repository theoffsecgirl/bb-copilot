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
bbcopilot ingest webxray out.jsonl
bbcopilot ingest takeovflow takeovers.jsonl
bbcopilot ingest pathraider lfi.jsonl
bbcopilot clusters
bbcopilot cluster-show --id C-0001
bbcopilot auto-triage
bbcopilot exploit-plan
bbcopilot report-top
```

## What it does

- Reads your local vault (Markdown playbooks by vuln type and phase)
- Sends the right context + your input to the configured model
- Returns structured, actionable output: hypotheses → steps → evidence → impact
- Generates complete reports ready to submit to HackerOne, Bugcrowd or YesWeHack
- Saves local history of all sessions in `~/.bbcopilot/history/`
- Stores normalized findings in `~/.bbcopilot/findings/`
- Correlates findings into scored clusters
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

## Usage

```bash
bbcopilot ask "target has GraphQL with user_id in mutations"
bbcopilot plan --target example.com --type web
bbcopilot vuln ssrf
bbcopilot triage --finding "open redirect on /redirect?url="
bbcopilot report --finding "IDOR on /api/v1/invoices/{id} exposes other users' invoices"
bbcopilot history
bbcopilot vault-list
```

## Findings workflow

This layer turns `bb-copilot` from a guided assistant into a workflow hub.

### 1. Ingest

```bash
bbcopilot ingest webxray out.jsonl
bbcopilot ingest takeovflow takeovers.jsonl
bbcopilot ingest pathraider lfi.jsonl
```

### 2. Review findings

```bash
bbcopilot findings
bbcopilot findings --tool webxray --vector xss --host api.example.com
```

### 3. Correlation v1

`bb-copilot` no longer just groups by host/vector. It builds **clusters** using:
- host
- vector
- param overlap
- multi-tool agreement
- severity and confidence

Each cluster exposes:
- `cluster_id`
- `score`
- `why_it_matters`
- `next_step`
- tools involved
- targets involved
- finding ids

```bash
bbcopilot correlate
bbcopilot clusters
bbcopilot cluster-show --id C-0001
```

### 4. Triage and exploit

```bash
bbcopilot auto-triage
bbcopilot exploit-plan
```

### 5. Report

```bash
bbcopilot report-id --id F-202604190001-0001
bbcopilot report-top -o top-report.md
```

## Example integration

```bash
webxray -u https://target.com --format jsonl --json-output web.jsonl
pathraider -u "https://target.com/download?file=FUZZ" --format jsonl --stdout > lfi.jsonl
takeovflow -d target.com --format jsonl --stdout > takeover.jsonl

bbcopilot ingest webxray web.jsonl
bbcopilot ingest pathraider lfi.jsonl
bbcopilot ingest takeovflow takeover.jsonl

bbcopilot clusters
bbcopilot cluster-show --id C-0001
bbcopilot exploit-plan
bbcopilot report-top
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
| `report-top` | — | Full report from top scored cluster |
| `ingest` | Tool name + JSON/JSONL | Normalize and persist findings |
| `findings` | Optional filters | List stored findings |
| `correlate` | — | Show scored correlations |
| `clusters` | — | List scored clusters |
| `cluster-show` | Cluster ID | Inspect one cluster |
| `auto-triage` | — | Triage top cluster |
| `exploit-plan` | — | Exploit/validation plan for top cluster |
| `history` | — | Last sessions in table |
| `vault-list` | — | List of available playbooks |

## Correlation model

A finding is a signal.
A cluster is a bug hypothesis.

The current correlator prioritizes:
- same host + same vector
- same host + same param + different vectors
- multiple tools agreeing on the same surface

This is enough to reduce noise and surface likely real bugs fast.

## Storage

- History: `~/.bbcopilot/history/`
- Findings: `~/.bbcopilot/findings/`

## Philosophy

- Result over explanation
- Always structured: hypotheses → checks → evidence → impact
- The vault is the brain. The model is the engine.
- Findings make the workflow reproducible.
- Clusters make the workflow actionable.
- No black boxes. The knowledge is yours.

---

By [@theoffsecgirl](https://github.com/theoffsecgirl)
