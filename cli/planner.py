from cli.vault import load_all, load_vuln, load_methodology, load_system_prompt
from cli.llm import ask
from cli.models import CopilotResponse
from pathlib import Path


def run_ask(observation: str) -> CopilotResponse:
    """Free-form question with full vault as context."""
    vault = load_all()
    system = load_system_prompt()
    return ask(system, observation, vault.content)


def run_plan(target_url: str, target_type: str, context_file: str | None = None) -> CopilotResponse:
    """Generate a full attack plan for a given target."""
    vault = load_all()
    system = load_system_prompt()

    extra = ""
    if context_file:
        p = Path(context_file)
        if p.exists():
            extra = f"\n\nAdditional context from file:\n{p.read_text()}"

    user_msg = (
        f"Generate a full bug bounty attack plan for:\n"
        f"Target: {target_url}\n"
        f"Type: {target_type}\n"
        f"{extra}\n\n"
        f"Follow the vault methodology. Prioritize by impact. Be specific and actionable."
    )
    return ask(system, user_msg, vault.content)


def run_vuln(vuln_name: str, context_file: str | None = None) -> CopilotResponse:
    """Get guided steps for a specific vulnerability class."""
    try:
        vuln_ctx = load_vuln(vuln_name)
    except FileNotFoundError as e:
        from cli.models import CopilotResponse
        return CopilotResponse(raw=str(e))

    method_ctx = load_methodology()
    system = load_system_prompt()

    extra = ""
    if context_file:
        p = Path(context_file)
        if p.exists():
            extra = f"\n\nAdditional context:\n{p.read_text()}"

    combined = vuln_ctx.content + method_ctx.content
    user_msg = (
        f"I want to hunt {vuln_name.upper()} vulnerabilities.\n"
        f"Give me the full testing methodology, priority checks, payloads and what high-impact findings look like.\n"
        f"{extra}"
    )
    return ask(system, user_msg, combined)


def run_triage(finding: str) -> CopilotResponse:
    """Triage a specific finding: impact, evidence needed, report structure."""
    vault = load_all()
    system = load_system_prompt()
    user_msg = (
        f"Triage this bug bounty finding:\n\n\"{finding}\"\n\n"
        f"Provide: severity estimate, potential impact, evidence needed to confirm, "
        f"next steps to escalate, and report structure."
    )
    return ask(system, user_msg, vault.content)
