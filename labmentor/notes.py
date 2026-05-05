from __future__ import annotations

from datetime import date
from pathlib import Path

from labmentor.models import LabState
from labmentor.recommendations import recommend_next_steps


def build_notes(state: LabState) -> str:
    recommendations = recommend_next_steps(state.services, state.target)
    service_rows = "\n".join(
        f"| {service.port}/{service.protocol} | {service.name} | {format_service_detail(service.product, service.version)} | |"
        for service in state.services
    )
    if not service_rows:
        service_rows = "| | | | |"

    lead_rows = "\n".join(
        f"| {lead.get('title', '')} | {lead.get('evidence', '')} | {lead.get('next_step', '')} | {lead.get('status', 'Open')} |"
        for lead in state.leads
    )
    if not lead_rows:
        lead_rows = "| | | | |"

    next_steps = []
    for rec in recommendations:
        command_block = "\n".join(f"  - `{command}`" for command in rec["commands"])
        look_for = "\n".join(f"  - {item}" for item in rec["look_for"])
        next_steps.append(
            f"### {rec['title']}\n\n"
            f"Why: {rec['why']}\n\n"
            f"Commands:\n{command_block}\n\n"
            f"Look for:\n{look_for}\n"
        )

    return f"""# Lab Notes: {state.name}

## Target

- Platform: {state.platform}
- Target: {state.target}
- Date: {date.today().isoformat()}
- Status: In progress

## Objective

Learn the attack path by documenting enumeration, leads, evidence, and methodology lessons.

## Open Ports and Services

| Port | Service | Version/Details | Notes |
|---|---|---|---|
{service_rows}

## Recommended Next Steps

{chr(10).join(next_steps)}

## Enumeration Notes

### Nmap

Command:

```bash
# paste your nmap command here
```

Summary:

- 

### Web

Commands:

```bash
# paste web enumeration commands here
```

Findings:

- 

### SMB / File Sharing

Commands:

```bash
# paste SMB enumeration commands here
```

Findings:

- 

### Other Services

Findings:

- 

## Leads

| Lead | Evidence | Next Step | Status |
|---|---|---|---|
{lead_rows}

## Initial Access

Vulnerability or weakness:

Evidence:

Steps:

```bash
# paste commands or manual steps here
```

Result:

- 

## Privilege Escalation

Current user:

Interesting findings:

- 

Path:

```bash
# paste commands or manual steps here
```

Result:

- 

## Walkthrough Comparison

Use this after importing a walkthrough and running `labmentor compare`.

## Lessons Learned

- 
"""


def format_service_detail(product: str, version: str) -> str:
    return f"{product} {version}".strip()


def write_notes(state: LabState, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(build_notes(state), encoding="utf-8")
    return path
