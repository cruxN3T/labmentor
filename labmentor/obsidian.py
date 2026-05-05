from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

from labmentor.models import LabState

CONFIG_ENV = "LABMENTOR_CONFIG_HOME"
CONFIG_FILE = "config.json"

PLATFORM_NAMES = {
    "offsec": "OffSec",
    "pg": "Proving-Grounds",
    "proving-grounds": "Proving-Grounds",
    "htb": "HTB",
    "hackthebox": "HTB",
    "thm": "TryHackMe",
    "tryhackme": "TryHackMe",
    "local": "Local",
}

ENGAGEMENT_DIRS = [
    "Scans",
    "Evidence",
    "Screenshots",
    "Loot",
    "Walkthroughs",
    "Walkthrough-Reviews",
    "Lessons",
]


def config_dir() -> Path:
    override = os.environ.get(CONFIG_ENV)
    if override:
        return Path(override).expanduser()
    return Path.home() / ".config" / "labmentor"


def config_path() -> Path:
    return config_dir() / CONFIG_FILE


def load_config() -> dict[str, Any]:
    path = config_path()
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save_config(config: dict[str, Any]) -> None:
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(config, indent=2), encoding="utf-8")


def set_vault_path(path: Path) -> Path:
    resolved = path.expanduser().resolve()
    resolved.mkdir(parents=True, exist_ok=True)
    config = load_config()
    config["vault_path"] = str(resolved)
    save_config(config)
    return resolved


def get_vault_path() -> Path:
    config = load_config()
    vault_path = config.get("vault_path")
    if not vault_path:
        raise FileNotFoundError("No Obsidian vault configured. Run `labmentor vault set <path>` first.")
    return Path(vault_path).expanduser()


def create_engagement_workspace(state: LabState) -> Path:
    lab_dir = vault_lab_dir(state)
    lab_dir.mkdir(parents=True, exist_ok=True)
    for directory in ENGAGEMENT_DIRS:
        (lab_dir / directory).mkdir(parents=True, exist_ok=True)
    return lab_dir


def vault_lab_dir(state: LabState) -> Path:
    return get_vault_path() / platform_dir(state.platform) / slugify(state.name)


def vault_note_path(state: LabState) -> Path:
    return vault_lab_dir(state) / f"{slugify(state.name)}.md"


def vault_scans_dir(state: LabState) -> Path:
    return vault_lab_dir(state) / "Scans"


def vault_evidence_dir(state: LabState) -> Path:
    return vault_lab_dir(state) / "Evidence"


def vault_comparison_path(state: LabState) -> Path:
    return vault_lab_dir(state) / "Walkthrough-Reviews" / f"{slugify(state.name)}-comparison.md"


def vault_lessons_path(state: LabState) -> Path:
    return vault_lab_dir(state) / "Lessons" / f"{slugify(state.name)}-lessons.md"


def write_obsidian_file(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def platform_dir(platform: str) -> str:
    normalized = slugify(platform).lower()
    return PLATFORM_NAMES.get(normalized, slugify(platform))


def slugify(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip())
    cleaned = re.sub(r"-+", "-", cleaned).strip("-._")
    return cleaned or "lab"
