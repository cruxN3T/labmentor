from __future__ import annotations

import shutil
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from labmentor.models import LabState
from labmentor.nmap_parser import parse_nmap_file
from labmentor.notes import write_notes
from labmentor.recommendations import recommend_next_steps
from labmentor.storage import load_state, save_state, workspace_root
from labmentor.walkthroughs import compare_notes_to_walkthrough, extract_lessons, import_walkthrough

app = typer.Typer(help="LabMentor: learn the path, not just the answer.")
console = Console()


@app.command()
def start(
    platform: Annotated[str, typer.Option(help="Training platform, such as offsec, pg, thm, htb, or local.")],
    name: Annotated[str, typer.Option(help="Lab, room, machine, or box name.")],
    target: Annotated[str, typer.Option(help="Target IP or hostname inside the authorized lab.")],
) -> None:
    """Create a local LabMentor workspace."""
    workspace = workspace_root()
    workspace.mkdir(parents=True, exist_ok=True)
    state = LabState(platform=platform, name=name, target=target, workspace=workspace)
    save_state(state)
    console.print(Panel.fit(f"Started LabMentor workspace for [bold]{name}[/bold] ({target})"))


@app.command()
def status() -> None:
    """Show the current LabMentor workspace status."""
    state = load_state()
    recommendations = recommend_next_steps(state.services, state.target)
    top_recommendation = recommendations[0]["title"] if recommendations else "No recommendation available"

    table = Table(title="LabMentor Status")
    table.add_column("Field", style="bold")
    table.add_column("Value")
    table.add_row("Lab", state.name)
    table.add_row("Platform", state.platform)
    table.add_row("Target", state.target)
    table.add_row("Workspace", str(state.workspace))
    table.add_row("Services imported", str(len(state.services)))
    table.add_row("Leads", str(len(state.leads)))
    table.add_row("Notes", str(state.notes_path) if state.notes_path else "Not generated")
    table.add_row(
        "Walkthrough",
        str(state.walkthrough_path) if state.walkthrough_path else "Not imported",
    )
    table.add_row("Next recommended path", str(top_recommendation))
    console.print(table)


@app.command()
def services() -> None:
    """List imported services for the current lab."""
    state = load_state()
    if not state.services:
        console.print("No services imported yet. Run `labmentor import-nmap <file>` first.")
        raise typer.Exit(code=0)

    table = Table(title="Imported Services")
    table.add_column("Port")
    table.add_column("State")
    table.add_column("Service")
    table.add_column("Details")
    for service in state.services:
        table.add_row(
            f"{service.port}/{service.protocol}",
            service.state,
            service.name,
            f"{service.product} {service.version}".strip(),
        )
    console.print(table)


@app.command()
def reset(
    yes: Annotated[bool, typer.Option("--yes", "-y", help="Confirm deletion without prompting.")] = False,
) -> None:
    """Delete the local .labmentor workspace for the current directory."""
    workspace = workspace_root()
    if not workspace.exists():
        console.print("No .labmentor workspace exists in this directory.")
        raise typer.Exit(code=0)

    if not yes:
        console.print(
            "This will delete the local .labmentor workspace for this directory. "
            "Run `labmentor reset --yes` to confirm."
        )
        raise typer.Exit(code=1)

    shutil.rmtree(workspace)
    console.print(f"Deleted workspace: [bold]{workspace}[/bold]")


@app.command("import-nmap")
def import_nmap(path: Annotated[Path, typer.Argument(help="Path to nmap output text file.")]) -> None:
    """Import nmap output and update the current lab state."""
    state = load_state()
    services = parse_nmap_file(path)
    state.services = services
    save_state(state)

    table = Table(title="Imported Services")
    table.add_column("Port")
    table.add_column("Service")
    table.add_column("Details")
    for service in services:
        table.add_row(f"{service.port}/{service.protocol}", service.name, f"{service.product} {service.version}".strip())
    console.print(table)


@app.command()
def next() -> None:  # noqa: A001 - CLI command name is intentional.
    """Show recommended next steps based on imported services."""
    state = load_state()
    recommendations = recommend_next_steps(state.services, state.target)
    for rec in recommendations:
        body = [f"[bold]Why:[/bold] {rec['why']}", "", "[bold]Run:[/bold]"]
        body.extend(f"  {command}" for command in rec["commands"])
        body.extend(["", "[bold]Look for:[/bold]"])
        body.extend(f"  - {item}" for item in rec["look_for"])
        console.print(Panel("\n".join(body), title=str(rec["title"]), expand=False))


@app.command()
def notes(output: Annotated[Path, typer.Option(help="Output notes path.")] = Path("notes.md")) -> None:
    """Generate Markdown lab notes."""
    state = load_state()
    notes_path = write_notes(state, output)
    state.notes_path = notes_path
    save_state(state)
    console.print(f"Wrote notes to [bold]{notes_path}[/bold]")


@app.command("add-lead")
def add_lead(
    title: Annotated[str, typer.Argument(help="Lead title, such as 'Anonymous SMB access'.")],
    evidence: Annotated[str, typer.Option(help="Evidence supporting the lead.")] = "",
    next_step: Annotated[str, typer.Option(help="Recommended next action.")] = "",
    status: Annotated[str, typer.Option(help="Lead status.")] = "Open",
) -> None:
    """Add a lead to the current lab state."""
    state = load_state()
    state.leads.append(
        {
            "title": title,
            "evidence": evidence,
            "next_step": next_step,
            "status": status,
        }
    )
    save_state(state)
    console.print(f"Added lead: [bold]{title}[/bold]")


@app.command("import-walkthrough")
def import_walkthrough_command(path: Annotated[Path, typer.Argument(help="Path to walkthrough Markdown or text file.")]) -> None:
    """Import a walkthrough for learning comparison."""
    state = load_state()
    destination = state.workspace / "walkthrough.md"
    import_walkthrough(path, destination)
    state.walkthrough_path = destination
    save_state(state)
    console.print(f"Imported walkthrough to [bold]{destination}[/bold]")


@app.command()
def compare(output: Annotated[Path, typer.Option(help="Comparison output path.")] = Path("walkthrough-comparison.md")) -> None:
    """Compare your notes against an imported walkthrough."""
    state = load_state()
    comparison = compare_notes_to_walkthrough(state)
    output.write_text(comparison, encoding="utf-8")
    console.print(f"Wrote walkthrough comparison to [bold]{output}[/bold]")


@app.command()
def lessons(output: Annotated[Path, typer.Option(help="Lessons output path.")] = Path("lessons-learned.md")) -> None:
    """Extract methodology lessons from the walkthrough comparison."""
    state = load_state()
    lesson_text = extract_lessons(state)
    output.write_text(lesson_text, encoding="utf-8")
    console.print(f"Wrote lessons learned to [bold]{output}[/bold]")


if __name__ == "__main__":
    app()
