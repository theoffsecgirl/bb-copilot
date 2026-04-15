import os
from pathlib import Path
from cli.models import VaultContext


VAULT_PATH = Path(os.getenv("VAULT_PATH", "./vault"))


def load_all() -> VaultContext:
    """Load entire vault as single context string."""
    files = []
    content_parts = []

    for md_file in sorted(VAULT_PATH.rglob("*.md")):
        rel_path = md_file.relative_to(VAULT_PATH)
        files.append(str(rel_path))
        text = md_file.read_text(encoding="utf-8")
        content_parts.append(f"\n\n--- {rel_path} ---\n{text}")

    return VaultContext(files=files, content="".join(content_parts))


def load_vuln(name: str) -> VaultContext:
    """Load a specific vulnerability playbook by name."""
    vuln_file = VAULT_PATH / "vulns" / f"{name.lower()}.md"
    if not vuln_file.exists():
        available = [f.stem for f in (VAULT_PATH / "vulns").glob("*.md")]
        raise FileNotFoundError(
            f"Playbook '{name}' not found. Available: {', '.join(available)}"
        )
    content = vuln_file.read_text(encoding="utf-8")
    return VaultContext(files=[str(vuln_file)], content=content)


def load_methodology() -> VaultContext:
    """Load only methodology files."""
    method_path = VAULT_PATH / "methodology"
    files = []
    parts = []
    for f in sorted(method_path.glob("*.md")):
        files.append(str(f))
        parts.append(f"\n\n--- {f.name} ---\n{f.read_text()}")
    return VaultContext(files=files, content="".join(parts))


def load_patterns() -> VaultContext:
    """Load pattern files."""
    pattern_path = VAULT_PATH / "patterns"
    files = []
    parts = []
    for f in sorted(pattern_path.glob("*.md")):
        files.append(str(f))
        parts.append(f"\n\n--- {f.name} ---\n{f.read_text()}")
    return VaultContext(files=files, content="".join(parts))


def load_system_prompt() -> str:
    prompt_file = VAULT_PATH / "prompts" / "system.txt"
    if prompt_file.exists():
        return prompt_file.read_text(encoding="utf-8")
    return "You are an expert bug bounty assistant. Be direct and actionable."
