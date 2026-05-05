from __future__ import annotations

import re
from pathlib import Path

from labmentor.models import Service

NMAP_SERVICE_LINE = re.compile(
    r"^(?P<port>\d+)/(?:tcp|udp)\s+(?P<state>open|filtered|closed|open\|filtered)\s+(?P<service>\S+)(?:\s+(?P<detail>.*))?$"
)


def parse_nmap_text(text: str) -> list[Service]:
    services: list[Service] = []

    for line in text.splitlines():
        stripped = line.strip()
        match = NMAP_SERVICE_LINE.match(stripped)
        if not match:
            continue

        proto = stripped.split()[0].split("/", maxsplit=1)[1]
        detail = (match.group("detail") or "").strip()
        product, version = split_detail(detail)
        services.append(
            Service(
                port=int(match.group("port")),
                protocol=proto,
                state=match.group("state"),
                name=match.group("service"),
                product=product,
                version=version,
                raw=stripped,
            )
        )

    return services


def parse_nmap_file(path: Path) -> list[Service]:
    return parse_nmap_text(path.read_text(encoding="utf-8", errors="ignore"))


def split_detail(detail: str) -> tuple[str, str]:
    if not detail:
        return "", ""
    parts = detail.split()
    if len(parts) <= 1:
        return detail, ""
    return parts[0], " ".join(parts[1:])
