from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from labmentor.models import LabState, Service

STATE_FILE = "state.json"


def workspace_root() -> Path:
    return Path.cwd() / ".labmentor"


def state_path() -> Path:
    return workspace_root() / STATE_FILE


def save_state(state: LabState) -> None:
    workspace_root().mkdir(parents=True, exist_ok=True)
    data = asdict(state)
    data["workspace"] = str(state.workspace)
    data["notes_path"] = str(state.notes_path) if state.notes_path else None
    data["walkthrough_path"] = str(state.walkthrough_path) if state.walkthrough_path else None
    state_path().write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_state() -> LabState:
    path = state_path()
    if not path.exists():
        raise FileNotFoundError("No LabMentor workspace found. Run `labmentor start` first.")

    data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    services = [Service(**service) for service in data.get("services", [])]
    notes_path = Path(data["notes_path"]) if data.get("notes_path") else None
    walkthrough_path = Path(data["walkthrough_path"]) if data.get("walkthrough_path") else None

    return LabState(
        platform=data["platform"],
        name=data["name"],
        target=data["target"],
        workspace=Path(data["workspace"]),
        services=services,
        leads=data.get("leads", []),
        notes_path=notes_path,
        walkthrough_path=walkthrough_path,
    )
