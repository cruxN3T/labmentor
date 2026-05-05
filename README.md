# LabMentor

**Learn the path, not just the answer.**

LabMentor is a pentest lab companion for learning methodology, note-taking, and walkthrough analysis across OffSec labs, Proving Grounds, TryHackMe, and Hack The Box.

It is designed for authorized training environments where you want to understand how to approach a lab like a better pentester: enumerate, identify leads, choose next steps, document evidence, and learn from walkthroughs after getting stuck.

## What LabMentor does

- Parses common `nmap` output
- Summarizes open services
- Recommends practical next steps
- Explains why a step matters
- Generates clean Markdown lab notes
- Tracks leads and next actions
- Imports walkthrough text or Markdown
- Compares your notes against a walkthrough
- Extracts methodology lessons from what you missed

## What LabMentor does not do

- It does not auto-exploit targets
- It does not submit flags
- It does not bypass platform rules
- It does not assist with certification exams where AI/LLM assistance is prohibited
- It does not target systems outside labs you are authorized to test

## Intended platforms

LabMentor is intended for authorized learning environments such as:

- OffSec labs and Proving Grounds
- TryHackMe rooms
- Hack The Box machines and Academy-style labs
- Local vulnerable VMs
- Private training ranges

Always follow the rules of the platform, course, lab, or engagement you are using.

## Install from source

```bash
git clone https://github.com/cruxN3T/labmentor.git
cd labmentor
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Quick start

Create a new lab workspace:

```bash
labmentor start --platform htb --name example-box --target 10.10.10.10
```

Import `nmap` output:

```bash
labmentor import-nmap scans/nmap.txt
```

Get recommended next steps:

```bash
labmentor next
```

Generate or update notes:

```bash
labmentor notes
```

Import a walkthrough after you get stuck:

```bash
labmentor import-walkthrough walkthrough.md
labmentor compare
labmentor lessons
```

## Example next-step output

```text
Current situation:
- 22/tcp SSH is open
- 80/tcp HTTP is open
- 445/tcp SMB is open

Recommended next step:
Start with SMB enumeration.

Why:
SMB often exposes shares, usernames, backups, or credentials in labs.

Run:
smbclient -L //TARGET -N
smbmap -H TARGET

Look for:
- readable shares
- backup files
- config files
- usernames
- credentials
```

## Project status

LabMentor is in early development. The first public version focuses on simple local workflows, Markdown notes, service-based next-step recommendations, and walkthrough comparison.

## Safety and ethics

Use LabMentor only in environments where you have authorization. The tool is built for learning methodology and improving note-taking, not for unauthorized access or automated exploitation.

## License

MIT License. See [LICENSE](LICENSE).
