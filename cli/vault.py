import os
from pathlib import Path
from cli.models import VaultContext

VAULT_PATH = Path(os.getenv("VAULT_PATH", "./vault"))
# 0 = sin límite. Reducir si usas Groq free tier (~5000)
MAX_CONTEXT_TOKENS = int(os.getenv("BBCOPILOT_MAX_CONTEXT_TOKENS", "0"))

# Estimación simple: ~4 chars por token
_CHARS_PER_TOKEN = 4


def _truncate(content: str) -> str:
    """Trunca el contenido si se ha definido un límite de tokens."""
    if MAX_CONTEXT_TOKENS == 0:
        return content
    max_chars = MAX_CONTEXT_TOKENS * _CHARS_PER_TOKEN
    if len(content) <= max_chars:
        return content
    return content[:max_chars] + "\n\n[... vault truncado por límite de tokens ...]"


def load_all() -> VaultContext:
    """Carga el vault completo como string de contexto."""
    files = []
    content_parts = []
    for md_file in sorted(VAULT_PATH.rglob("*.md")):
        rel_path = md_file.relative_to(VAULT_PATH)
        files.append(str(rel_path))
        text = md_file.read_text(encoding="utf-8")
        content_parts.append(f"\n\n--- {rel_path} ---\n{text}")
    return VaultContext(files=files, content=_truncate("".join(content_parts)))


def load_vuln(name: str) -> VaultContext:
    """Carga el playbook de una vulnerabilidad concreta."""
    vuln_file = VAULT_PATH / "vulns" / f"{name.lower()}.md"
    if not vuln_file.exists():
        available = [f.stem for f in (VAULT_PATH / "vulns").glob("*.md")]
        raise FileNotFoundError(
            f"Playbook '{name}' no encontrado. Disponibles: {', '.join(sorted(available))}"
        )
    content = vuln_file.read_text(encoding="utf-8")
    return VaultContext(files=[str(vuln_file)], content=content)


def load_methodology() -> VaultContext:
    """Carga solo los ficheros de metodología."""
    method_path = VAULT_PATH / "methodology"
    files, parts = [], []
    for f in sorted(method_path.glob("*.md")):
        files.append(str(f))
        parts.append(f"\n\n--- {f.name} ---\n{f.read_text()}")
    return VaultContext(files=files, content="".join(parts))


def load_patterns() -> VaultContext:
    """Carga los ficheros de patrones."""
    pattern_path = VAULT_PATH / "patterns"
    files, parts = [], []
    for f in sorted(pattern_path.glob("*.md")):
        files.append(str(f))
        parts.append(f"\n\n--- {f.name} ---\n{f.read_text()}")
    return VaultContext(files=files, content="".join(parts))


def load_system_prompt() -> str:
    prompt_file = VAULT_PATH / "prompts" / "system.txt"
    if prompt_file.exists():
        return prompt_file.read_text(encoding="utf-8")
    return "Eres un asistente experto en bug bounty. Sé directo y accionable."
