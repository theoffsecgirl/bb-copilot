import json
import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
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
def ask(
    observation: str = typer.Argument(..., help="Observación o pregunta sobre un target"),
    full: bool = typer.Option(False, "--full", "-f", help="Output detallado completo"),
    save: bool = typer.Option(True, "--save/--no-save", help="Guardar en historial"),
) -> None:
    from cli.planner import run_ask
    from cli.history import save as save_history
    mode = "[dim][full][/dim]" if full else "[dim][compact][/dim]"
    console.print(Panel(f"[bold cyan]Pregunta:[/bold cyan] {observation} {mode}", expand=False))
    with console.status("[bold green]Pensando...[/bold green]"):
        result = run_ask(observation, full=full)
    _print_response(result.raw, result.tokens_used)
    if save:
        path = save_history("ask", observation, result)
        console.print(f"[dim]Guardado en {path}[/dim]")


@app.command()
def plan(
    target: str = typer.Option(..., "--target", "-t", help="URL o dominio del target"),
    type: str = typer.Option("web", "--type", help="Tipo: web | api | mobile"),
    context: Optional[str] = typer.Option(None, "--context", "-c", help="Fichero de contexto"),
    full: bool = typer.Option(False, "--full", help="Output detallado completo"),
    save: bool = typer.Option(True, "--save/--no-save", help="Guardar en historial"),
) -> None:
    from cli.planner import run_plan
    from cli.history import save as save_history
    mode = "[dim][full][/dim]" if full else "[dim][compact][/dim]"
    console.print(Panel(f"[bold cyan]Plan:[/bold cyan] {target} [{type}] {mode}", expand=False))
    with console.status("[bold green]Construyendo plan...[/bold green]"):
        result = run_plan(target, type, context, full=full)
    _print_response(result.raw, result.tokens_used)
    if save:
        path = save_history("plan", f"{target} [{type}]", result)
        console.print(f"[dim]Guardado en {path}[/dim]")


@app.command()
def vuln(
    name: str = typer.Argument(..., help="Clase de vuln: idor, ssrf, xss, cors..."),
    context: Optional[str] = typer.Option(None, "--context", "-c", help="Fichero de contexto"),
    full: bool = typer.Option(False, "--full", help="Output detallado completo"),
    save: bool = typer.Option(True, "--save/--no-save", help="Guardar en historial"),
) -> None:
    from cli.planner import run_vuln
    from cli.history import save as save_history
    mode = "[dim][full][/dim]" if full else "[dim][compact][/dim]"
    console.print(Panel(f"[bold cyan]Vuln:[/bold cyan] {name.upper()} {mode}", expand=False))
    with console.status("[bold green]Cargando playbook...[/bold green]"):
        result = run_vuln(name, context, full=full)
    _print_response(result.raw, result.tokens_used)
    if save:
        path = save_history("vuln", name, result)
        console.print(f"[dim]Guardado en {path}[/dim]")


@app.command()
def triage(
    finding: str = typer.Option(..., "--finding", help="Hallazgo a triar"),
    full: bool = typer.Option(False, "--full", help="Output detallado completo"),
    save: bool = typer.Option(True, "--save/--no-save", help="Guardar en historial"),
) -> None:
    from cli.planner import run_triage
    from cli.history import save as save_history
    mode = "[dim][full][/dim]" if full else "[dim][compact][/dim]"
    console.print(Panel(f"[bold cyan]Triage:[/bold cyan] {finding} {mode}", expand=False))
    with console.status("[bold green]Triando...[/bold green]"):
        result = run_triage(finding, full=full)
    _print_response(result.raw, result.tokens_used)
    if save:
        path = save_history("triage", finding, result)
        console.print(f"[dim]Guardado en {path}[/dim]")


@app.command(name="triage-id")
def triage_id(
    finding_id: str = typer.Option(..., "--id", help="ID del finding"),
) -> None:
    from cli.findings import find_by_id
    from cli.planner import run_triage
    finding = find_by_id(finding_id)
    if not finding:
        console.print("[red]Finding no encontrado[/red]")
        raise typer.Exit(code=1)
    result = run_triage(json.dumps(finding, ensure_ascii=False, indent=2), full=True)
    _print_response(result.raw, result.tokens_used)


@app.command()
def report(
    finding: str = typer.Option(..., "--finding", help="Descripción del hallazgo"),
    target: Optional[str] = typer.Option(None, "--target", "-t", help="Target"),
    context: Optional[str] = typer.Option(None, "--context", "-c", help="Fichero con requests/notas"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Guardar en fichero .md"),
    save: bool = typer.Option(True, "--save/--no-save", help="Guardar en historial"),
) -> None:
    from cli.reporter import run_report
    from cli.history import save as save_history
    console.print(Panel(f"[bold cyan]Reporte:[/bold cyan] {finding}", expand=False))
    with console.status("[bold green]Generando reporte...[/bold green]"):
        result = run_report(finding, context, target)
    _print_response(result.raw, result.tokens_used)
    if output:
        out_file = output if output.endswith(".md") else output + ".md"
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(result.raw)
        console.print(f"[green]Reporte guardado en {out_file}[/green]")
    if save:
        path = save_history("report", finding, result)
        console.print(f"[dim]Guardado en historial: {path}[/dim]")


@app.command(name="report-id")
def report_id(
    finding_id: str = typer.Option(..., "--id", help="ID del finding"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Guardar en fichero .md"),
) -> None:
    from cli.findings import find_by_id
    from cli.reporter import run_report
    finding = find_by_id(finding_id)
    if not finding:
        console.print("[red]Finding no encontrado[/red]")
        raise typer.Exit(code=1)
    result = run_report(json.dumps(finding, ensure_ascii=False, indent=2))
    _print_response(result.raw, result.tokens_used)
    if output:
        out_file = output if output.endswith(".md") else output + ".md"
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(result.raw)
        console.print(f"[green]Reporte guardado en {out_file}[/green]")


@app.command(name="report-top")
def report_top(
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Guardar en fichero .md"),
) -> None:
    from cli.findings import correlate_findings
    from cli.reporter import run_report
    results = correlate_findings()
    if not results:
        console.print("[dim]No se encontraron correlaciones[/dim]")
        raise typer.Exit(code=1)
    top = results[0]
    result = run_report(json.dumps(top, ensure_ascii=False, indent=2))
    _print_response(result.raw, result.tokens_used)
    if output:
        out_file = output if output.endswith(".md") else output + ".md"
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(result.raw)
        console.print(f"[green]Reporte guardado en {out_file}[/green]")


@app.command()
def history(
    last: int = typer.Option(10, "--last", "-n", help="Número de entradas"),
    clear: bool = typer.Option(False, "--clear", help="Borrar todo el historial"),
) -> None:
    from cli.history import load_last, clear as clear_history
    if clear:
        n = clear_history()
        console.print(f"[yellow]Historial borrado ({n} entradas).[/yellow]")
        return
    entries = load_last(last)
    if not entries:
        console.print("[dim]No hay entradas en el historial.[/dim]")
        return
    table = Table(title=f"Últimas {len(entries)} entradas", show_lines=True)
    table.add_column("Fecha", style="dim", width=20)
    table.add_column("Comando", style="cyan", width=10)
    table.add_column("Input", style="white")
    table.add_column("Tokens", style="dim", width=8)
    for e in entries:
        ts = e.get("timestamp", "")[:19].replace("T", " ")
        cmd = e.get("command", "")
        inp = e.get("input", "")[:80] + ("..." if len(e.get("input", "")) > 80 else "")
        tokens = str(e.get("tokens", ""))
        table.add_row(ts, cmd, inp, tokens)
    console.print(table)


@app.command(name="vault-list")
def vault_list() -> None:
    from cli.vault import load_all
    ctx = load_all()
    console.print("[bold]Vault — playbooks disponibles:[/bold]")
    for f in ctx.files:
        console.print(f"  [green]✓[/green] {f}")
    console.print(f"\n[dim]{len(ctx.files)} ficheros cargados[/dim]")


@app.command()
def ingest(
    tool: str = typer.Argument(..., help="Nombre de la tool origen"),
    input_file: str = typer.Argument(..., help="Fichero JSON/JSONL de entrada"),
) -> None:
    from cli.findings import ingest_file
    count, path = ingest_file(tool, input_file)
    console.print(f"[green]Importados {count} findings[/green]")
    console.print(f"[dim]{path}[/dim]")


@app.command()
def findings(
    tool: Optional[str] = typer.Option(None, "--tool", help="Filtrar por tool"),
    vector: Optional[str] = typer.Option(None, "--vector", help="Filtrar por vector"),
    host: Optional[str] = typer.Option(None, "--host", help="Filtrar por host"),
    limit: int = typer.Option(50, "--limit", help="Máximo de resultados a mostrar"),
) -> None:
    from cli.findings import load_all_findings
    data = load_all_findings()
    if tool:
        data = [f for f in data if f.get("tool") == tool]
    if vector:
        data = [f for f in data if f.get("vector") == vector]
    if host:
        data = [f for f in data if f.get("host") == host]
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
        console.print(f"[yellow]{c['host']}[/yellow] [{c['vector']}] → {c['count']} findings | score={c.get('score', 0)}")
        console.print(f"  tools: {', '.join(c['tools'])}")
        for t in c['targets'][:3]:
            console.print(f"    - {t}")


@app.command()
def clusters(
    limit: int = typer.Option(20, "--limit", help="Máximo de clusters a mostrar"),
) -> None:
    from cli.findings import build_clusters
    results = build_clusters()
    if not results:
        console.print("[dim]No clusters[/dim]")
        return
    for c in results[:limit]:
        console.print(f"[bold cyan]{c['cluster_id']}[/bold cyan] {c['host']} [{c['vector']}] score={c['score']}")
        console.print(f"  tools: {', '.join(c['tools'])}")
        if c.get('params'):
            console.print(f"  params: {', '.join(c['params'])}")
        console.print(f"  why: {c['why_it_matters']}")
        console.print(f"  next: {c['next_step']}")


@app.command(name="cluster-show")
def cluster_show(
    cluster_id: str = typer.Option(..., "--id", help="ID del cluster"),
) -> None:
    from cli.findings import get_cluster
    cluster = get_cluster(cluster_id)
    if not cluster:
        console.print("[red]Cluster no encontrado[/red]")
        raise typer.Exit(code=1)
    console.print(json.dumps(cluster, ensure_ascii=False, indent=2))


@app.command(name="auto-triage")
def auto_triage() -> None:
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


@app.command(name="exploit-plan")
def exploit_plan() -> None:
    from cli.findings import correlate_findings
    from cli.planner import run_exploit_plan
    results = correlate_findings()
    if not results:
        console.print("[dim]No correlations found[/dim]")
        return
    top = results[0]
    summary = json.dumps(top, ensure_ascii=False, indent=2)
    console.print(f"[bold red]Exploit planning:[/bold red] {top['host']} [{top['vector']}]")
    result = run_exploit_plan(summary, full=True)
    _print_response(result.raw, result.tokens_used)


if __name__ == "__main__":
    app()
