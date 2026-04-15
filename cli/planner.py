from cli.vault import load_all, load_vuln, load_methodology, load_system_prompt, load_patterns, VAULT_PATH
from cli.llm import ask
from cli.models import CopilotResponse, VaultContext
from pathlib import Path


# Mapa de palabras clave → ficheros del vault
_KEYWORD_MAP: dict[str, list[str]] = {
    # vulns
    "idor": ["vulns/idor.md"],
    "ssrf": ["vulns/ssrf.md"],
    "xss": ["vulns/xss.md"],
    "sqli": ["vulns/sqli.md", "vulns/sqli.md"],
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
    # patterns
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
    # methodology
    "recon": ["methodology/recon.md"],
    "js": ["methodology/js-analysis.md"],
    "javascript": ["methodology/js-analysis.md"],
    "api": ["methodology/api-hunting.md"],
    "graphql": ["methodology/api-hunting.md", "vulns/idor.md"],
    "report": ["methodology/reporting.md"],
    "scope": ["methodology/asset-triage.md"],
}


def _smart_context(text: str) -> VaultContext:
    """Carga solo los ficheros del vault relevantes para el input dado."""
    text_lower = text.lower()
    matched_files: list[str] = []

    for keyword, files in _KEYWORD_MAP.items():
        if keyword in text_lower:
            for f in files:
                if f not in matched_files:
                    matched_files.append(f)

    # Siempre incluir el system prompt
    parts = []
    for rel_path in matched_files:
        full_path = VAULT_PATH / rel_path
        if full_path.exists():
            parts.append(f"\n\n--- {rel_path} ---\n{full_path.read_text()}")

    # Si no hay match, cargar vault completo (fallback)
    if not parts:
        return load_all()

    return VaultContext(files=matched_files, content="".join(parts))


def run_ask(observation: str) -> CopilotResponse:
    """Pregunta libre. Carga solo los playbooks relevantes según el input."""
    ctx = _smart_context(observation)
    system = load_system_prompt()
    return ask(system, observation, ctx.content)


def run_plan(target_url: str, target_type: str, context_file: str | None = None) -> CopilotResponse:
    """Plan de ataque completo para un target."""
    # Para plan cargamos methodology completa + patterns
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
        f"Genera un plan de ataque completo de bug bounty para:\n"
        f"Target: {target_url}\n"
        f"Tipo: {target_type}\n"
        f"{extra}\n\n"
        f"Sigue la metodología del vault. Prioriza por impacto. Sé específico y accionable."
    )
    return ask(system, user_msg, combined)


def run_vuln(vuln_name: str, context_file: str | None = None) -> CopilotResponse:
    """Playbook completo para una clase de vulnerabilidad."""
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
        f"Quiero buscar vulnerabilidades {vuln_name.upper()}.\n"
        f"Dame la metodología completa de testing, checks prioritarios, payloads y cómo se ve un hallazgo de alto impacto.\n"
        f"{extra}"
    )
    # Solo el playbook específico — sin cargar todo el vault
    return ask(system, user_msg, vuln_ctx.content)


def run_triage(finding: str) -> CopilotResponse:
    """Triage de un hallazgo: severidad, impacto, evidencia, siguientes pasos."""
    ctx = _smart_context(finding)
    system = load_system_prompt()
    user_msg = (
        f"Tria este hallazgo de bug bounty:\n\n\"{finding}\"\n\n"
        f"Proporciona: estimación de severidad, impacto potencial, evidencia necesaria para confirmar, "
        f"siguientes pasos para escalar y estructura del reporte."
    )
    return ask(system, user_msg, ctx.content)
