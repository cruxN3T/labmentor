# Roadmap

LabMentor is an early-stage pentest lab training companion. The goal is to help learners build better methodology, notes, and walkthrough review habits without becoming dependent on copy/paste answers.

## v0.1 - Initial scaffold

- [x] Python package scaffold
- [x] CLI entrypoint
- [x] Local workspace state
- [x] Basic Nmap parser
- [x] Service-based next-step recommendations
- [x] Markdown notes generator
- [x] Walkthrough import
- [x] Notes-vs-walkthrough comparison
- [x] Lessons-learned output
- [x] Basic tests

## v0.2 - Better lab workflow

- [x] Add `labmentor status`
- [x] Add `labmentor services`
- [x] Add `labmentor reset` with confirmation
- [x] Add `labmentor workspace`
- [x] Add placeholder warnings for commands that need lab-specific values
- [x] Add methodology checklists for web, Linux privilege escalation, Windows privilege escalation, and Active Directory
- [ ] Add workspace profiles per lab instead of one `.labmentor` state per directory
- [ ] Add support for importing Grepable Nmap and XML Nmap output
- [ ] Improve notes update behavior so existing notes are not overwritten accidentally
- [ ] Add JSON lead export

## v0.3 - More methodology coverage

- [x] Add service modules for SNMP and NFS
- [x] Add Windows/Active Directory service guidance for LDAP, Kerberos, SMB, and WinRM
- [ ] Add service modules for SMTP, RPC, MSSQL, MySQL, PostgreSQL, Redis, and RDP
- [ ] Expand Linux privilege escalation checklist generator
- [ ] Expand Windows privilege escalation checklist generator
- [ ] Expand Active Directory lab checklist generator
- [ ] Expand web app checklist generator

## v0.4 - Walkthrough learning improvements

- [ ] Improve walkthrough comparison beyond keyword checks
- [ ] Add missed-step categories
- [ ] Add methodology checklist updates from lessons
- [ ] Add support for retired-machine review mode
- [ ] Add `labmentor explain` for pasted command output

## v1.0 - Stable public release

- [ ] Stable CLI interface
- [ ] Documentation site or expanded docs
- [ ] Example complete lab workflow
- [ ] Packaged release
- [ ] Contribution guidelines finalized
