# bb-copilot

> Asistente de bug bounty con IA. Vault + CLI + workflow de findings y correlación real.

> 🇬🇧 [English version](README.md)

```bash
bbcopilot ingest webxray out.jsonl
bbcopilot ingest takeovflow takeovers.jsonl
bbcopilot ingest pathraider lfi.jsonl
bbcopilot clusters
bbcopilot cluster-show --id C-0001
bbcopilot auto-triage
bbcopilot exploit-plan
```

## Qué hace

- Usa tu vault local (playbooks en Markdown)
- Genera output estructurado: hipótesis → pasos → evidencia → impacto
- Guarda historial en `~/.bbcopilot/history/`
- Almacena findings en `~/.bbcopilot/findings/`
- Correlaciona findings en clusters con score
- NO automatiza ataques

---

## Workflow de findings

### 1. Ingestar

```bash
bbcopilot ingest webxray out.jsonl
bbcopilot ingest takeovflow takeovers.jsonl
bbcopilot ingest pathraider lfi.jsonl
```

### 2. Revisar

```bash
bbcopilot findings
```

### 3. Correlación v1 (clave)

El sistema ya no agrupa solo por host/vector.

Ahora crea **clusters** usando:
- host
- vector
- parámetros
- múltiples tools
- severidad y confidence

Cada cluster incluye:
- cluster_id
- score
- why_it_matters
- next_step

```bash
bbcopilot correlate
bbcopilot clusters
bbcopilot cluster-show --id C-0001
```

### 4. Triage y explotación

```bash
bbcopilot auto-triage
bbcopilot exploit-plan
```

### 5. Reporte

```bash
bbcopilot report-top
```

---

## Ejemplo real

```bash
webxray -u https://target.com --format jsonl --stdout > web.jsonl
pathraider -u "https://target.com/download?file=FUZZ" --format jsonl --stdout > lfi.jsonl

bbcopilot ingest webxray web.jsonl
bbcopilot ingest pathraider lfi.jsonl

bbcopilot clusters
```

Salida:

```text
C-0001 target.com [lfd_traversal+xss] score=95
why: mismo parámetro afectado por múltiples vectores
next: probar /etc/passwd y escalar
```

---

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
| correlate | Correlacionar |
| clusters | Listar clusters |
| cluster-show | Ver cluster |
| auto-triage | Triage automático |
| exploit-plan | Plan de explotación |

---

## Modelo mental

finding → señal
cluster → hipótesis de bug

---

## Filosofía

- Resultado > explicación
- Clusters > findings
- Menos ruido, más impacto
