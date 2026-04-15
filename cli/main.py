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
    """Pregunta libre. Compacto por defecto, --full para output completo."""
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
    """Plan de ataque completo. Compacto por defecto, --full para más detalle."""
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
    """Playbook de una vulnerabilidad. Compacto por defecto."""
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
    """Triage de un hallazgo. Compacto por defecto."""
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


@app.command()
def report(
    finding: str = typer.Option(..., "--finding", help="Descripción del hallazgo"),
    target: Optional[str] = typer.Option(None, "--target", "-t", help="Target"),
    context: Optional[str] = typer.Option(None, "--context", "-c", help="Fichero con requests/notas"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Guardar en fichero .md"),
    save: bool = typer.Option(True, "--save/--no-save", help="Guardar en historial"),
) -> None:
    """Reporte completo listo para HackerOne/Bugcrowd/YesWeHack."""
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


@app.command()
def history(
    last: int = typer.Option(10, "--last", "-n", help="Número de entradas"),
    clear: bool = typer.Option(False, "--clear", help="Borrar todo el historial"),
) -> None:
    """Ver o gestionar el historial de sesiones."""
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
    """Lista todos los playbooks disponibles en el vault."""
    from cli.vault import load_all
    ctx = load_all()
    console.print("[bold]Vault — playbooks disponibles:[/bold]")
    for f in ctx.files:
        console.print(f"  [green]✓[/green] {f}")
    console.print(f"\n[dim]{len(ctx.files)} ficheros cargados[/dim]")


if __name__ == "__main__":
    app()
