from dataclasses import dataclass, field


@dataclass
class VaultContext:
    files: list[str] = field(default_factory=list)
    content: str = ""


@dataclass
class CopilotResponse:
    raw: str = ""
    tokens_used: int = 0
