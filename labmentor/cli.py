from __future__ import annotations

import shutil
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from labmentor.checklists import get_checklist, valid_checklists
from labmentor.models import LabState
from labmentor.nmap_parser import parse_nmap_file
from labmentor.notes import build_notes, write_notes
from labmentor.obsidian import (
    create_engagement_workspace,
    get_vault_path,
    set_vault_path,
    vault_comparison_path,
    vault_evidence_dir,
    vault_lessons_path,
    vault_note_path,
    vault_scans_dir,
    write_obsidian_file,
)
from labmentor.recommendations import recommend_next_steps
from labmentor.storage import load_state, save_state, state_path, workspace_root
from labmentor.walkthroughs import compare_notes_to_walkthrough, extract_lessons, import_walkthrough

app = typer.Typer(help="LabMentor: learn the path, not just the answer.")
vault_app = typer.Typer(help="Configure Obsidian vault export support.")
app.add_typer(vault_app, name="vault")
console = Console()

PLACEHOLDER_HELP = {
    "LAB.LOCAL": "replace with the real domain name, such as example.local",
    "users.txt": "replace with the path to an existing username wordlist",
    "USER": "replace with a valid username after credentials are found",
    "PASS": "replace with a valid password after credentials are found",
    "<user>": "replace with a valid username after credentials are found",
    "<export>": "replace with the NFS export path from showmount output",
    "<ports>": "replace with the discovered comma-separated ports",
}


@app.command()
def start(
    platform: Annotated[str, typer.Option(help="Training platform, such as offsec, pg, thm, htb, or local.")],
    name: Annotated[str, typer.Option(help="Lab, room, machine, or box name.")],
    target: Annotated[str, typer.Option(help="Target IP, hostname, or subnet inside the authorized lab.")],
    obsidian: Annotated[bool, typer.Option("--obsidian", help="Create and update an Obsidian engagement folder.")] = False,
) -> None:
    """Create a local LabMentor workspace."""
    workspace = workspace_root()
    workspace.mkdir(parents=True, exist_ok=True)
    state = LabState(platform=platform, name=name, target=target, workspace=workspace)

    if obsidian:
        lab_dir = create_engagement_workspace(state)
        state.notes_path = write_obsidian_file(vault_note_path(state), build_notes(state))
        save_state(state)
        console.print(Panel.fit(f"Started LabMentor workspace for [bold]{name}[/bold] ({target})"))
        console.print(f"Created Obsidian engagement folder: [bold]{lab_dir}[/bold]")
        console.print(f"Wrote notes to [bold]{state.notes_path}[/bold]")
        return

    save_state(state)
    console.print(Panel.fit(f"Started LabMentor workspace for [bold]{name}[/bold] ({target})"))


@vault_app.command("set")
def vault_set(path: Annotated[Path, typer.Argument(help="Path to your Obsidian vault or LabMentor folder inside it.")]) -> None:
    """Set the Obsidian vault path for LabMentor exports."""
    resolved = set_vault_path(path)
    console.print(f"Obsidian vault path set to [bold]{resolved}[/bold]")


@vault_app.command("show")
def vault_show() -> None:
    """Show the configured Obsidian vault path."""
    try:
        vault_path = get_vault_path()
    except FileNotFoundError as error:
        console.print(str(error))
        raise typer.Exit(code=1) from error

    table = Table(title="LabMentor Obsidian Vault")
    table.add_column("Item", style="bold")
    table.add_column("Value")
    table.add_row("Vault path", str(vault_path))
    table.add_row("Status", "exists" if vault_path.exists() else "missing")
    console.print(table)


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
    table.add_row("Walkthrough", str(state.walkthrough_path) if state.walkthrough_path else "Not imported")
    table.add_row("Next recommended path", str(top_recommendation))
    console.print(table)


@app.command()
def workspace() -> None:
    """Show local LabMentor workspace paths and file status."""
    root = workspace_root()
    state_file = state_path()

    table = Table(title="LabMentor Workspace")
    table.add_column("Item", style="bold")
    table.add_column("Path")
    table.add_column("Status")
    table.add_row("Workspace", str(root), "exists" if root.exists() else "missing")
    table.add_row("State file", str(state_file), "exists" if state_file.exists() else "missing")

    if state_file.exists():
        state = load_state()
        table.add_row("Notes", str(state.notes_path) if state.notes_path else "not configured", "exists" if state.notes_path and state.notes_path.exists() else "missing/not generated")
        table.add_row("Walkthrough", str(state.walkthrough_path) if state.walkthrough_path else "not imported", "exists" if state.walkthrough_path and state.walkthrough_path.exists() else "missing/not imported")

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
        table.add_row(f"{service.port}/{service.protocol}", service.state, service.name, f"{service.product} {service.version}".strip())
    console.print(table)


@app.command()
def checklist(
    type: Annotated[str, typer.Option("--type", "-t", help="Checklist type. Valid values: web, linux-privesc, windows-privesc, ad.")] = "web",
) -> None:
    """Show a methodology checklist."""
    try:
        items = get_checklist(type)
    except KeyError as error:
        console.print(str(error).strip('"'))
        console.print(f"Valid checklists: {', '.join(valid_checklists())}")
        raise typer.Exit(code=1) from error

    table = Table(title=f"{type} Checklist")
    table.add_column("#", justify="right")
    table.add_column("Step")
    for index, item in enumerate(items, start=1):
        table.add_row(str(index), item)
    console.print(table)


@app.command()
def reset(yes: Annotated[bool, typer.Option("--yes", "-y", help="Confirm deletion without prompting.")] = False) -> None:
    """Delete the local .labmentor workspace for the current directory."""
    workspace_path = workspace_root()
    if not workspace_path.exists():
        console.print("No .labmentor workspace exists in this directory.")
        raise typer.Exit(code=0)

    if not yes:
        console.print("This will delete the local .labmentor workspace for this directory. Run `labmentor reset --yes` to confirm.")
        raise typer.Exit(code=1)

    shutil.rmtree(workspace_path)
    console.print(f"Deleted workspace: [bold]{workspace_path}[/bold]")


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
    auto_update_obsidian(state)


@app.command("import-scan")
def import_scan(path: Annotated[Path, typer.Argument(help="Path to a scan file to copy into the Obsidian engagement Scans folder.")]) -> None:
    """Copy a scan artifact into the Obsidian engagement folder."""
    state = load_state()
    destination = vault_scans_dir(state) / path.name
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, destination)
    console.print(f"Copied scan to [bold]{destination}[/bold]")
    auto_update_obsidian(state)


@app.command("import-evidence")
def import_evidence(path: Annotated[Path, typer.Argument(help="Path to an evidence file to copy into the Obsidian engagement Evidence folder.")]) -> None:
    """Copy an evidence artifact into the Obsidian engagement folder."""
    state = load_state()
    destination = vault_evidence_dir(state) / path.name
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, destination)
    console.print(f"Copied evidence to [bold]{destination}[/bold]")
    auto_update_obsidian(state)


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

        placeholder_notes = detect_placeholder_notes(rec["commands"])
        if placeholder_notes:
            body.extend(["", "[bold yellow]Replace before running:[/bold yellow]"])
            body.extend(f"  - {note}" for note in placeholder_notes)

        console.print(Panel("\n".join(body), title=str(rec["title"]), expand=False))


@app.command()
def notes(
    output: Annotated[Path, typer.Option(help="Output notes path.")] = Path("notes.md"),
    obsidian: Annotated[bool, typer.Option("--obsidian", help="Write notes to the configured Obsidian vault.")] = False,
) -> None:
    """Generate Markdown lab notes."""
    state = load_state()
    if obsidian:
        create_engagement_workspace(state)
        notes_path = write_obsidian_file(vault_note_path(state), build_notes(state))
    else:
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
    state.leads.append({"title": title, "evidence": evidence, "next_step": next_step, "status": status})
    save_state(state)
    console.print(f"Added lead: [bold]{title}[/bold]")
    auto_update_obsidian(state)


@app.command("import-walkthrough")
def import_walkthrough_command(path: Annotated[Path, typer.Argument(help="Path to walkthrough Markdown or text file.")]) -> None:
    """Import a walkthrough for learning comparison."""
    state = load_state()
    destination = state.workspace / "walkthrough.md"
    import_walkthrough(path, destination)
    state.walkthrough_path = destination
    save_state(state)
    console.print(f"Imported walkthrough to [bold]{destination}[/bold]")
    auto_update_obsidian(state)


@app.command()
def compare(
    output: Annotated[Path, typer.Option(help="Comparison output path.")] = Path("walkthrough-comparison.md"),
    obsidian: Annotated[bool, typer.Option("--obsidian", help="Write comparison to the configured Obsidian vault.")] = False,
) -> None:
    """Compare your notes against an imported walkthrough."""
    state = load_state()
    comparison = compare_notes_to_walkthrough(state)
    output_path = write_obsidian_file(vault_comparison_path(state), comparison) if obsidian else output
    if not obsidian:
        output_path.write_text(comparison, encoding="utf-8")
    console.print(f"Wrote walkthrough comparison to [bold]{output_path}[/bold]")


@app.command()
def lessons(
    output: Annotated[Path, typer.Option(help="Lessons output path.")] = Path("lessons-learned.md"),
    obsidian: Annotated[bool, typer.Option("--obsidian", help="Write lessons to the configured Obsidian vault.")] = False,
) -> None:
    """Extract methodology lessons from the walkthrough comparison."""
    state = load_state()
    lesson_text = extract_lessons(state)
    output_path = write_obsidian_file(vault_lessons_path(state), lesson_text) if obsidian else output
    if not obsidian:
        output_path.write_text(lesson_text, encoding="utf-8")
    console.print(f"Wrote lessons learned to [bold]{output_path}[/bold]")


def auto_update_obsidian(state: LabState) -> None:
    if state.notes_path and is_inside_vault(state.notes_path):
        create_engagement_workspace(state)
        write_obsidian_file(vault_note_path(state), build_notes(state))


def is_inside_vault(path: Path) -> bool:
    try:
        path.resolve().relative_to(get_vault_path().resolve())
        return True
    except (FileNotFoundError, ValueError):
        return False


def detect_placeholder_notes(commands: list[str]) -> list[str]:
    notes: list[str] = []
    joined = "\n".join(commands)
    for placeholder, guidance in PLACEHOLDER_HELP.items():
        if placeholder in joined:
            notes.append(f"{placeholder}: {guidance}")
    return notes


if __name__ == "__main__":
    app()
