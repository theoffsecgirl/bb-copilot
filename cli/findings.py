import json
import os
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

FINDINGS_DIR = Path(os.getenv("BBCOPILOT_FINDINGS_DIR", "~/.bbcopilot/findings")).expanduser()


def _ensure_dir() -> None:
    FINDINGS_DIR.mkdir(parents=True, exist_ok=True)


def _gen_id(index: int) -> str:
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"F-{ts}-{index:04d}"


def _gen_cluster_id(index: int) -> str:
    return f"C-{index:04d}"


def _iter_input_records(file_path: str) -> list[dict[str, Any]]:
    path = Path(file_path)
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []
    if path.suffix.lower() == ".jsonl":
        records: list[dict[str, Any]] = []
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            records.append(obj if isinstance(obj, dict) else {"value": obj})
        return records
    data = json.loads(text)
    if isinstance(data, list):
        return [item if isinstance(item, dict) else {"value": item} for item in data]
    if isinstance(data, dict):
        records = []
        for key, value in data.items():
            if isinstance(value, list):
                for item in value:
                    obj = item if isinstance(item, dict) else {"value": item}
                    obj.setdefault("type", key)
                    records.append(obj)
            else:
                obj = value if isinstance(value, dict) else {"value": value}
                obj.setdefault("type", key)
                records.append(obj)
        return records
    return [{"value": data}]


def _derive_host(item: dict[str, Any]) -> str | None:
    if item.get("host"):
        return item.get("host")
    target = item.get("target") or item.get("url")
    if not target:
        return None
    try:
        return urlparse(str(target)).netloc or None
    except Exception:
        return None


def normalize_records(tool: str, file_path: str) -> list[dict[str, Any]]:
    raw_records = _iter_input_records(file_path)
    now = datetime.now().isoformat()
    normalized: list[dict[str, Any]] = []
    for idx, item in enumerate(raw_records, start=1):
        entry = {
            "id": _gen_id(idx),
            "tool": tool,
            "type": item.get("type", "unknown"),
            "vector": item.get("vector"),
            "target": item.get("target") or item.get("url") or item.get("host"),
            "host": _derive_host(item),
            "method": item.get("method"),
            "param": item.get("param"),
            "severity": str(item.get("severity", "info")).lower(),
            "confidence": str(item.get("confidence", "low")).lower(),
            "reason": item.get("reason"),
            "evidence": item.get("evidence", []),
            "tags": item.get("tags", []),
            "raw": item,
            "timestamp": item.get("timestamp", now),
        }
        normalized.append(entry)
    return normalized


def save_findings(tool: str, findings: list[dict[str, Any]]) -> Path:
    _ensure_dir()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = FINDINGS_DIR / f"{ts}_{tool}.jsonl"
    with output_path.open("w", encoding="utf-8") as f:
        for item in findings:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    return output_path


def ingest_file(tool: str, file_path: str) -> tuple[int, Path]:
    findings = normalize_records(tool, file_path)
    output_path = save_findings(tool, findings)
    return len(findings), output_path


def load_all_findings() -> list[dict[str, Any]]:
    _ensure_dir()
    results: list[dict[str, Any]] = []
    for file in sorted(FINDINGS_DIR.glob("*.jsonl")):
        with file.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    results.append(json.loads(line))
                except Exception:
                    continue
    return results


def find_by_id(finding_id: str) -> dict[str, Any] | None:
    for finding in load_all_findings():
        if finding.get("id") == finding_id:
            return finding
    return None


def _deduplicate_findings(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, str, str, str]] = set()
    unique: list[dict[str, Any]] = []
    for f in findings:
        key = (
            str(f.get("host") or ""),
            str(f.get("vector") or f.get("type") or ""),
            str(f.get("param") or ""),
            str(f.get("target") or ""),
        )
        if key in seen:
            continue
        seen.add(key)
        unique.append(f)
    return unique


def _score_cluster(items: list[dict[str, Any]]) -> int:
    score = 0
    severity_map = {"critical": 90, "high": 70, "medium": 50, "low": 30, "info": 10}
    confidence_map = {"high": 15, "medium": 8, "low": 2}
    tools = {str(i.get('tool', 'unknown')) for i in items}
    params = {str(i.get('param')) for i in items if i.get('param')}
    severities = [severity_map.get(str(i.get("severity", "info")).lower(), 10) for i in items]
    confidences = [confidence_map.get(str(i.get("confidence", "low")).lower(), 2) for i in items]
    score += max(severities) if severities else 0
    score += max(confidences) if confidences else 0
    score += max(0, (len(tools) - 1) * 20)
    if len(params) == 1 and params:
        score += 30
    if len(items) >= 3:
        score += 10
    return min(score, 100)


def _why_it_matters(items: list[dict[str, Any]]) -> str:
    tools = sorted({str(i.get('tool', 'unknown')) for i in items})
    params = sorted({str(i.get('param')) for i in items if i.get('param')})
    vectors = sorted({str(i.get('vector') or i.get('type') or 'unknown') for i in items})
    if len(tools) > 1 and len(params) == 1 and params:
        return f"same param flagged across multiple tools ({', '.join(tools)})"
    if len(tools) > 1:
        return f"multiple tools agree on the same host/vector ({', '.join(tools)})"
    return f"repeated signals for vector(s): {', '.join(vectors)}"


def _next_step(items: list[dict[str, Any]]) -> str:
    vectors = {str(i.get('vector') or i.get('type') or '').lower() for i in items}
    if 'lfd_traversal' in vectors:
        return 'validate with /etc/passwd or win.ini and then test escalation paths like /proc/self/environ or log poisoning'
    if 'subdomain_takeover' in vectors:
        return 'verify provider claim path, dangling DNS state and takeover confirmation page/body'
    if 'xss' in vectors:
        return 'confirm execution context, sink type and try auth-impacting pages'
    if 'sqli' in vectors:
        return 'confirm with controlled error/time-based payloads and minimize PoC'
    return 'manually validate the strongest finding in the cluster and look for impact amplification'


def build_clusters(findings: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    findings = _deduplicate_findings(findings or load_all_findings())
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    param_grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)

    for finding in findings:
        host = finding.get("host") or "unknown-host"
        vector = finding.get("vector") or finding.get("type") or "unknown"
        grouped[(str(host), str(vector))].append(finding)
        if finding.get("param"):
            param_grouped[(str(host), str(finding.get('param')))].append(finding)

    clusters: list[dict[str, Any]] = []
    cluster_index = 1

    for (host, vector), items in grouped.items():
        if len(items) < 2:
            continue
        clusters.append({
            "cluster_id": _gen_cluster_id(cluster_index),
            "host": host,
            "vector": vector,
            "params": sorted({str(i.get('param')) for i in items if i.get('param')}),
            "tools": sorted({str(i.get('tool', 'unknown')) for i in items}),
            "finding_ids": [i.get('id') for i in items],
            "targets": sorted({str(i.get('target')) for i in items if i.get('target')}),
            "score": _score_cluster(items),
            "why_it_matters": _why_it_matters(items),
            "next_step": _next_step(items),
            "evidence_summary": [str(i.get('reason') or '') for i in items if i.get('reason')][:5],
        })
        cluster_index += 1

    for (host, param), items in param_grouped.items():
        tools = {str(i.get('tool', 'unknown')) for i in items}
        vectors = {str(i.get('vector') or i.get('type') or 'unknown') for i in items}
        if len(items) < 2 or len(vectors) < 2:
            continue
        clusters.append({
            "cluster_id": _gen_cluster_id(cluster_index),
            "host": host,
            "vector": "+".join(sorted(vectors)),
            "params": [param],
            "tools": sorted(tools),
            "finding_ids": [i.get('id') for i in items],
            "targets": sorted({str(i.get('target')) for i in items if i.get('target')}),
            "score": min(_score_cluster(items) + 15, 100),
            "why_it_matters": f"same param flagged with multiple vectors on {host}",
            "next_step": _next_step(items),
            "evidence_summary": [str(i.get('reason') or '') for i in items if i.get('reason')][:5],
        })
        cluster_index += 1

    clusters.sort(key=lambda x: x["score"], reverse=True)
    return clusters


def correlate_findings() -> list[dict[str, Any]]:
    clusters = build_clusters()
    simplified: list[dict[str, Any]] = []
    for c in clusters:
        simplified.append(
            {
                "host": c["host"],
                "vector": c["vector"],
                "count": len(c["finding_ids"]),
                "ids": c["finding_ids"],
                "tools": c["tools"],
                "targets": c["targets"],
                "score": c["score"],
            }
        )
    return simplified


def get_cluster(cluster_id: str) -> dict[str, Any] | None:
    for cluster in build_clusters():
        if cluster.get("cluster_id") == cluster_id:
            return cluster
    return None
