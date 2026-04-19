import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

FINDINGS_DIR = Path(os.getenv("BBCOPILOT_FINDINGS_DIR", "~/.bbcopilot/findings")).expanduser()


def _ensure_dir() -> None:
    FINDINGS_DIR.mkdir(parents=True, exist_ok=True)


def _gen_id(index: int) -> str:
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"F-{ts}-{index:04d}"


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
            if isinstance(obj, dict):
                records.append(obj)
            else:
                records.append({"value": obj})
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
            "host": item.get("host"),
            "method": item.get("method"),
            "param": item.get("param"),
            "severity": item.get("severity", "info"),
            "confidence": item.get("confidence", "low"),
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
