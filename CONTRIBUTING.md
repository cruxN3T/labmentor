# Contributing to LabMentor

Thanks for considering a contribution. LabMentor is focused on helping people learn pentest lab methodology, note-taking, and walkthrough review.

## Project scope

Good contributions include:

- Better service enumeration guidance
- Better note templates
- Better walkthrough comparison logic
- Safer lab workflow features
- Documentation and examples
- Tests
- Bug fixes

Out of scope contributions include:

- Autonomous exploitation
- Payload generation for real targets
- Flag submission automation
- Platform rule bypasses
- Exam assistance workflows
- Features designed for unauthorized systems

## Development setup

```bash
git clone https://github.com/cruxN3T/labmentor.git
cd labmentor
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
ruff check .
```

## Pull request checklist

Before opening a pull request:

- Run `pytest`
- Run `ruff check .`
- Add or update tests where appropriate
- Update docs if the behavior changes
- Keep recommendations focused on authorized labs and learning

## Style

LabMentor should sound like a practical mentor:

- explain what to do
- explain why it matters
- explain what to look for
- avoid copy/paste answer dumping
- avoid unnecessary gatekeeping or quizzes
