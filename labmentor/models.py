from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class Service:
    port: int
    protocol: str
    state: str
    name: str
    product: str = ""
    version: str = ""
    raw: str = ""

    @property
    def label(self) -> str:
        parts = [f"{self.port}/{self.protocol}", self.name]
        detail = " ".join(part for part in [self.product, self.version] if part).strip()
        if detail:
            parts.append(detail)
        return " ".join(parts)


@dataclass(slots=True)
class LabState:
    platform: str
    name: str
    target: str
    workspace: Path
    services: list[Service] = field(default_factory=list)
    leads: list[dict[str, Any]] = field(default_factory=list)
    notes_path: Path | None = None
    walkthrough_path: Path | None = None
