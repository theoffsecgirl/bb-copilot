from cli.vault import load_all, load_vuln, load_methodology, load_system_prompt, load_patterns, VAULT_PATH
from cli.llm import ask
from cli.models import CopilotResponse, VaultContext
from pathlib import Path


_KEYWORD_MAP: dict[str, list[str]] = {
    "idor": ["vulns/idor.md"],
    "ssrf": ["vulns/ssrf.md"],
    "xss": ["vulns/xss.md"],
    "sqli": ["vulns/sqli.md"],
    "sql": ["vulns/sqli.md"],
    "cors": ["vulns/cors.md"],
    "xxe": ["vulns/xxe.md"],
    "ssti": ["vulns/ssti.md"],
    "template": ["vulns/ssti.md"],
    "oauth": ["vulns/oauth.md"],
    "redirect": ["vulns/open-redirect.md"],
    "upload": ["vulns/file-upload.md"],
    "takeover": ["vulns/subdomain-takeover.md"],
    "subdomain": ["vulns/subdomain-takeover.md"],
    "business": ["vulns/business-logic.md"],
    "logic": ["vulns/business-logic.md"],
    "jwt": ["patterns/auth-bypass.md", "patterns/role-confusion.md"],
    "token": ["patterns/auth-bypass.md"],
    "auth": ["patterns/auth-bypass.md"],
    "role": ["patterns/role-confusion.md"],
    "admin": ["patterns/role-confusion.md", "patterns/auth-bypass.md"],
    "tenant": ["patterns/multi-tenant.md"],
    "org": ["patterns/multi-tenant.md", "vulns/idor.md"],
    "org_id": ["patterns/multi-tenant.md", "vulns/idor.md"],
    "race": ["patterns/race-conditions.md"],
    "coupon": ["patterns/race-conditions.md", "vulns/business-logic.md"],
    "recon": ["methodology/recon.md"],
    "js": ["methodology/js-analysis.md"],
    "javascript": ["methodology/js-analysis.md"],
    "api": ["methodology/api-hunting.md"],
    "graphql": ["methodology/api-hunting.md", "vulns/idor.md"],
    "report": ["methodology/reporting.md"],
    "scope": ["methodology/asset-triage.md"],
}


def _smart_context(text: str) -> VaultContext:
    text_lower = text.lower()
    matched_files: list[str] = []
    for keyword, files in _KEYWORD_MAP.items():
        if keyword in text_lower:
            for f in files:
                if f not in matched_files:
                    matched_files.append(f)
    parts = []
    for rel_path in matched_files:
        full_path = VAULT_PATH / rel_path
        if full_path.exists():
            parts.append(f"\n\n--- {rel_path} ---\n{full_path.read_text()}")
    if not parts:
        return load_all()
    return VaultContext(files=matched_files, content="".join(parts))


def _mode_instruction(full: bool) -> str:
    return "Use MODE: FULL" if full else "Use MODE: COMPACT"


def run_ask(observation: str, full: bool = False) -> CopilotResponse:
    ctx = _smart_context(observation)
    system = load_system_prompt()
    msg = f"{_mode_instruction(full)}\n\n{observation}"
    return ask(system, msg, ctx.content)


def run_plan(target_url: str, target_type: str, context_file: str | None = None, full: bool = False) -> CopilotResponse:
    method_ctx = load_methodology()
    pattern_ctx = load_patterns()
    system = load_system_prompt()
    extra = ""
    if context_file:
        p = Path(context_file)
        if p.exists():
            extra = f"\n\nContexto adicional:\n{p.read_text()}"
    combined = method_ctx.content + pattern_ctx.content
    user_msg = (
        f"{_mode_instruction(full)}\n\n"
        f"Genera un plan de ataque completo de bug bounty para:\n"
        f"Target: {target_url}\nTipo: {target_type}\n{extra}\n\n"
        f"Sigue la metodología del vault. Prioriza por impacto. Sé específico y accionable."
    )
    return ask(system, user_msg, combined)


def run_vuln(vuln_name: str, context_file: str | None = None, full: bool = False) -> CopilotResponse:
    try:
        vuln_ctx = load_vuln(vuln_name)
    except FileNotFoundError as e:
        return CopilotResponse(raw=str(e))
    system = load_system_prompt()
    extra = ""
    if context_file:
        p = Path(context_file)
        if p.exists():
            extra = f"\n\nContexto adicional:\n{p.read_text()}"
    user_msg = (
        f"{_mode_instruction(full)}\n\n"
        f"Quiero buscar vulnerabilidades {vuln_name.upper()}.\n"
        f"Dame la metodología completa de testing, checks prioritarios, payloads y cómo se ve un hallazgo de alto impacto.\n"
        f"{extra}"
    )
    return ask(system, user_msg, vuln_ctx.content)


def run_triage(finding: str, full: bool = False) -> CopilotResponse:
    ctx = _smart_context(finding)
    system = load_system_prompt()
    user_msg = (
        f"{_mode_instruction(full)}\n\n"
        f"Tria este hallazgo de bug bounty:\n\n\"{finding}\"\n\n"
        f"Proporciona: estimación de severidad, impacto potencial, evidencia necesaria para confirmar, "
        f"siguientes pasos para escalar y estructura del reporte."
    )
    return ask(system, user_msg, ctx.content)


def run_exploit_plan(finding: str, full: bool = True) -> CopilotResponse:
    ctx = _smart_context(finding)
    system = load_system_prompt()
    user_msg = (
        f"{_mode_instruction(full)}\n\n"
        f"Genera un plan de explotación y validación para este hallazgo priorizado:\n\n{finding}\n\n"
        f"Devuelve exactamente estas secciones:\n"
        f"1. Hipótesis de explotación\n"
        f"2. Qué indica cada señal observada\n"
        f"3. Payloads o mutaciones concretas a probar\n"
        f"4. Pasos de validación en orden\n"
        f"5. Indicadores de confirmación\n"
        f"6. Variantes del vector\n"
        f"7. Impacto probable\n"
        f"8. Qué buscar después\n\n"
        f"No automatices ataques. Prioriza PoC mínima, reproducible y segura."
    )
    return ask(system, user_msg, ctx.content)
