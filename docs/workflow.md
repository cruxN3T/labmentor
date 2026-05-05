# LabMentor Workflow

LabMentor is built around a simple learning workflow:

```text
enumerate -> identify leads -> choose next step -> document evidence -> compare with walkthrough -> extract lessons
```

## 1. Start a workspace

```bash
labmentor start --platform htb --name example-box --target 10.10.10.10
```

This creates a local `.labmentor/state.json` file in your current directory.

## 2. Import scan output

```bash
labmentor import-nmap scans/nmap.txt
```

LabMentor parses common open service lines from standard Nmap output.

## 3. Ask for next steps

```bash
labmentor next
```

The tool recommends practical next steps based on open services. It explains:

- what to run
- why it matters
- what to look for

## 4. Generate notes

```bash
labmentor notes --output notes.md
```

The generated notes are meant to be edited as you work.

## 5. Track leads

```bash
labmentor add-lead "Anonymous SMB access" --evidence "smbclient -L worked with -N" --next-step "List and download readable shares"
```

Then regenerate notes:

```bash
labmentor notes --output notes.md
```

## 6. Learn from a walkthrough

After you are stuck or after solving the lab, import a walkthrough:

```bash
labmentor import-walkthrough walkthrough.md
labmentor compare
labmentor lessons
```

This creates:

- `walkthrough-comparison.md`
- `lessons-learned.md`

## Design philosophy

LabMentor should help you understand the path. It should not replace the process of learning or violate platform rules.
