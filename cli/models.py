from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Target:
    url: str
    type: str = "web"  # web | api | mobile
    notes: Optional[str] = None


@dataclass
class VaultContext:
    files: list[str] = field(default_factory=list)
    content: str = ""


@dataclass
class CopilotResponse:
    raw: str
    tokens_used: int = 0
