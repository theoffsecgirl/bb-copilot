import typer
from rich.console import Console
from rich.markdown import Markdown
from typing import Optional

app = typer.Typer(
    name="bbcopilot",
    help="Asistente de bug bounty con IA. Vault propio. Output estructurado.",
    add_completion=False,
)
console = Console()


def _print_response(raw: str, tokens: int = 0) -> None:
    console.print(Markdown(raw))
    if tokens:
        console.print(f"\n[dim]tokens usados: {tokens}[/dim]")


@app.command()
def ingest(tool: str, file: str) -> None:
    from cli.findings import ingest_file
    count, path = ingest_file(tool, file)
    console.print(f"[green]Imported {count} findings[/green]")
    console.print(f"[dim]{path}[/dim]")


@app.command()
def findings(limit: int = 50) -> None:
    from cli.findings import load_all_findings
    data = load_all_findings()
    if not data:
        console.print("[dim]No findings[/dim]")
        return
    for f in data[:limit]:
        console.print(f"[cyan]{f.get('id')}[/cyan] {f.get('type')} {f.get('tool')} {f.get('target')}")


@app.command()
def correlate() -> None:
    from cli.findings import correlate_findings
    results = correlate_findings()
    if not results:
        console.print("[dim]No correlations found[/dim]")
        return
    for c in results:
        console.print(f"[yellow]{c['host']}[/yellow] [{c['vector']}] → {c['count']} findings")
        console.print(f"  tools: {', '.join(c['tools'])}")
        for t in c['targets'][:3]:
            console.print(f"    - {t}")


@app.command(name="auto-triage")
def auto_triage() -> None:
    import json
    from cli.findings import correlate_findings
    from cli.planner import run_triage

    results = correlate_findings()
    if not results:
        console.print("[dim]No correlations found[/dim]")
        return

    top = results[0]
    summary = json.dumps(top, ensure_ascii=False, indent=2)
    console.print(f"[bold cyan]Auto-triaging top correlation:[/bold cyan] {top['host']} [{top['vector']}]")
    result = run_triage(summary, full=True)
    _print_response(result.raw, result.tokens_used)


@app.command(name="report-id")
def report_id(finding_id: str, output: Optional[str] = None) -> None:
    import json
    from cli.findings import find_by_id
    from cli.reporter import run_report

    finding = find_by_id(finding_id)
    if not finding:
        console.print("[red]Finding not found[/red]")
        return

    desc = json.dumps(finding, ensure_ascii=False, indent=2)
    result = run_report(desc)
    _print_response(result.raw, result.tokens_used)

    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(result.raw)


if __name__ == "__main__":
    app()
