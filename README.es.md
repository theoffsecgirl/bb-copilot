# bb-copilot

> Asistente de bug bounty con IA. Vault de metodología + CLI clásica + workflow de findings.

> 🇬🇧 [English version](README.md)

```bash
bbcopilot ask "api.target.com usa JWT y org_id en cada request"
bbcopilot plan --target api.target.com --type api
bbcopilot vuln idor --context notas.txt
bbcopilot triage --finding "IDOR en /api/v1/invoices/{id}"
bbcopilot ingest webxray out.jsonl
bbcopilot correlate
bbcopilot auto-triage
bbcopilot exploit-plan
```

## Qué hace

- Lee tu vault local (playbooks en Markdown por tipo de vuln y fase)
- Envía el contexto adecuado + tu input al modelo configurado
- Devuelve output estructurado y accionable: hipótesis → pasos → evidencia → impacto
- Genera reportes completos listos para enviar a HackerOne, Bugcrowd o YesWeHack
- Guarda historial local en `~/.bbcopilot/history/`
- Almacena findings normalizados en `~/.bbcopilot/findings/`
- Correlaciona findings de tools externas para priorizar superficies calientes
- NO automatiza ataques. Guía tu razonamiento

## Instalación

```bash
git clone https://github.com/theoffsecgirl/bb-copilot
cd bb-copilot
make setup
```

## Uso

```bash
bbcopilot ask "GraphQL con user_id"
bbcopilot plan --target api.example.com --type api
bbcopilot vuln idor
bbcopilot triage --finding "open redirect"
bbcopilot report --finding "IDOR en /api/v1/invoices/{id}"
bbcopilot history
bbcopilot vault-list
```

## Workflow de findings

```bash
# 1. Ingestar output de tools externas
bbcopilot ingest webxray out.jsonl

# 2. Revisar findings
bbcopilot findings
bbcopilot findings --tool webxray --vector xss --host api.example.com

# 3. Correlacionar
bbcopilot correlate

# 4. Triage automático
bbcopilot auto-triage

# 5. Plan de explotación
bbcopilot exploit-plan

# 6. Reportes
bbcopilot report-id --id F-...
bbcopilot report-top
```

## Ejemplo de integración

```bash
webxray -u https://target.com --format jsonl --json-output out.jsonl
bbcopilot ingest webxray out.jsonl
bbcopilot correlate
bbcopilot auto-triage
bbcopilot exploit-plan
```

## Comandos

| Comando | Descripción |
|---|---|
| ask | Pregunta libre |
| plan | Plan de ataque |
| vuln | Playbook |
| triage | Triage manual |
| triage-id | Triage desde finding |
| report | Reporte completo |
| report-id | Reporte desde finding |
| report-top | Reporte del cluster principal |
| ingest | Importar findings |
| findings | Listar findings |
| correlate | Correlacionar findings |
| auto-triage | Triage automático |
| exploit-plan | Plan de explotación |
| history | Historial |
| vault-list | Vault |

## Filosofía

- Resultado > explicación
- Workflow reproducible
- El vault es el cerebro
- Los findings son la memoria
