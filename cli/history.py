import json
import os
from datetime import datetime
from pathlib import Path
from cli.models import CopilotResponse

HISTORY_DIR = Path(os.getenv("BBCOPILOT_HISTORY_DIR", "~/.bbcopilot/history")).expanduser()


def _ensure_dir() -> None:
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)


def save(command: str, input_text: str, response: CopilotResponse) -> Path:
    """Guarda una entrada en el historial."""
    _ensure_dir()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    entry = {
        "timestamp": datetime.now().isoformat(),
        "command": command,
        "input": input_text,
        "response": response.raw,
        "tokens": response.tokens_used,
    }
    filepath = HISTORY_DIR / f"{ts}_{command}.json"
    filepath.write_text(json.dumps(entry, ensure_ascii=False, indent=2))
    return filepath


def load_last(n: int = 10) -> list[dict]:
    """Carga las últimas N entradas del historial."""
    _ensure_dir()
    files = sorted(HISTORY_DIR.glob("*.json"), reverse=True)[:n]
    entries = []
    for f in files:
        try:
            entries.append(json.loads(f.read_text()))
        except Exception:
            continue
    return entries


def load_by_id(entry_id: str) -> dict | None:
    """Carga una entrada específica por timestamp o nombre de fichero."""
    _ensure_dir()
    matches = list(HISTORY_DIR.glob(f"*{entry_id}*.json"))
    if not matches:
        return None
    return json.loads(matches[0].read_text())


def clear() -> int:
    """Borra todo el historial. Devuelve el número de entradas borradas."""
    _ensure_dir()
    files = list(HISTORY_DIR.glob("*.json"))
    for f in files:
        f.unlink()
    return len(files)
