from __future__ import annotations

import re
from pathlib import Path

from labmentor.models import LabState


def import_walkthrough(source: Path, destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(source.read_text(encoding="utf-8", errors="ignore"), encoding="utf-8")
    return destination


def compare_notes_to_walkthrough(state: LabState) -> str:
    if not state.notes_path or not state.notes_path.exists():
        raise FileNotFoundError("No notes found. Run `labmentor notes` first.")
    if not state.walkthrough_path or not state.walkthrough_path.exists():
        raise FileNotFoundError("No walkthrough found. Run `labmentor import-walkthrough <file>` first.")

    notes = normalize(state.notes_path.read_text(encoding="utf-8", errors="ignore"))
    walkthrough = normalize(state.walkthrough_path.read_text(encoding="utf-8", errors="ignore"))

    signals = build_signal_checks()
    missed: list[tuple[str, str, str]] = []
    matched: list[str] = []

    for label, patterns, lesson in signals:
        in_walkthrough = any(re.search(pattern, walkthrough) for pattern in patterns)
        in_notes = any(re.search(pattern, notes) for pattern in patterns)
        if in_walkthrough and not in_notes:
            missed.append((label, lesson, patterns[0]))
        elif in_walkthrough and in_notes:
            matched.append(label)

    matched_block = "\n".join(f"- {item}" for item in matched) or "- No obvious matched signals detected yet."
    missed_block = "\n".join(
        f"### {label}\n\nWhat likely happened:\n{lesson}\n" for label, lesson, _ in missed
    ) or "No obvious missed signals detected from the current rule set. Review manually for lab-specific logic."

    return f"""# Walkthrough Comparison: {state.name}

## Where Your Notes Matched the Walkthrough

{matched_block}

## What You May Have Missed

{missed_block}

## How to Use This

Do not treat this as a grading system. Treat it as a methodology review. If a signal appears here, add a checklist item so you recognize it earlier next time.
"""


def extract_lessons(state: LabState) -> str:
    comparison = compare_notes_to_walkthrough(state)
    lessons: list[str] = []

    if "SMB anonymous or share enumeration" in comparison:
        lessons.append("When SMB is open, test anonymous access, list shares, download readable files, and search them for credentials or paths.")
    if "Web directory or file discovery" in comparison:
        lessons.append("When HTTP is open, run content discovery with useful extensions and inspect backup/config/source files.")
    if "Credential reuse" in comparison:
        lessons.append("When you find credentials, test reuse across SSH, SMB, web logins, sudo, and service-specific panels where allowed.")
    if "Privilege escalation enumeration" in comparison:
        lessons.append("After initial access, enumerate sudo, SUID, capabilities, cron, services, writable paths, and interesting home/app files.")

    if not lessons:
        lessons.append("Review the walkthrough path and add one concrete checklist item for the first step you missed.")

    return "# Lessons Learned\n\n" + "\n".join(f"- {lesson}" for lesson in lessons) + "\n"


def normalize(text: str) -> str:
    return text.lower()


def build_signal_checks() -> list[tuple[str, list[str], str]]:
    return [
        (
            "SMB anonymous or share enumeration",
            [r"smbclient", r"smbmap", r"anonymous", r"share"],
            "The walkthrough appears to use SMB enumeration. Add SMB null-session and share review to your checklist whenever ports 139/445 are open.",
        ),
        (
            "Web directory or file discovery",
            [r"feroxbuster", r"gobuster", r"ffuf", r"dirb", r"backup", r"\.zip", r"\.bak"],
            "The walkthrough appears to rely on web content discovery or backup/source files. Add extension-based web discovery and source review to your checklist.",
        ),
        (
            "Credential reuse",
            [r"ssh .*@", r"password", r"credential", r"creds", r"login"],
            "The walkthrough appears to reuse discovered credentials. Add credential reuse testing across exposed services where the lab allows it.",
        ),
        (
            "Privilege escalation enumeration",
            [r"sudo -l", r"suid", r"linpeas", r"winpeas", r"capabilities", r"cron"],
            "The walkthrough appears to use privilege escalation enumeration. Add a post-access checklist for sudo, SUID, capabilities, cron, services, and writable paths.",
        ),
    ]
