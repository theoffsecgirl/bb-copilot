import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from typing import Optional

app = typer.Typer(
    name="bbcopilot",
    help="AI-powered bug bounty assistant. Vault-guided. Structured output.",
    add_completion=False,
)
console = Console()


def _print_response(raw: str, tokens: int = 0) -> None:
    console.print(Markdown(raw))
    if tokens:
        console.print(f"\n[dim]tokens used: {tokens}[/dim]")


@app.command()
def ask(
    observation: str = typer.Argument(..., help="Observation or question about a target"),
) -> None:
    """Ask anything. Full vault context is loaded automatically."""
    from cli.planner import run_ask
    console.print(Panel(f"[bold cyan]Asking:[/bold cyan] {observation}", expand=False))
    with console.status("[bold green]Thinking...[/bold green]"):
        result = run_ask(observation)
    _print_response(result.raw, result.tokens_used)


@app.command()
def plan(
    target: str = typer.Option(..., "--target", "-t", help="Target URL or domain"),
    type: str = typer.Option("web", "--type", help="Target type: web | api | mobile"),
    context: Optional[str] = typer.Option(None, "--context", "-c", help="Path to context file"),
) -> None:
    """Generate a full attack plan for a target."""
    from cli.planner import run_plan
    console.print(Panel(f"[bold cyan]Plan:[/bold cyan] {target} [{type}]", expand=False))
    with console.status("[bold green]Building plan...[/bold green]"):
        result = run_plan(target, type, context)
    _print_response(result.raw, result.tokens_used)


@app.command()
def vuln(
    name: str = typer.Argument(..., help="Vulnerability class (e.g. idor, ssrf, xss)"),
    context: Optional[str] = typer.Option(None, "--context", "-c", help="Path to context file"),
) -> None:
    """Get the playbook and guided checks for a specific vulnerability."""
    from cli.planner import run_vuln
    console.print(Panel(f"[bold cyan]Vuln:[/bold cyan] {name.upper()}", expand=False))
    with console.status("[bold green]Loading playbook...[/bold green]"):
        result = run_vuln(name, context)
    _print_response(result.raw, result.tokens_used)


@app.command()
def triage(
    finding: str = typer.Option(..., "--finding", "-f", help="Description of the finding to triage"),
) -> None:
    """Triage a finding: severity, impact, evidence needed, report structure."""
    from cli.planner import run_triage
    console.print(Panel(f"[bold cyan]Triage:[/bold cyan] {finding}", expand=False))
    with console.status("[bold green]Triaging...[/bold green]"):
        result = run_triage(finding)
    _print_response(result.raw, result.tokens_used)


@app.command()
def vault_list() -> None:
    """List all playbooks available in the vault."""
    from cli.vault import load_all
    ctx = load_all()
    console.print("[bold]Vault contents:[/bold]")
    for f in ctx.files:
        console.print(f"  [green]✓[/green] {f}")


if __name__ == "__main__":
    app()
