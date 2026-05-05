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

- [ ] Add `labmentor status`
- [ ] Add `labmentor services`
- [ ] Add `labmentor reset` with confirmation
- [ ] Add workspace profiles per lab instead of one `.labmentor` state per directory
- [ ] Add support for importing Grepable Nmap and XML Nmap output
- [ ] Improve notes update behavior so existing notes are not overwritten accidentally
- [ ] Add JSON lead export

## v0.3 - More methodology coverage

- [ ] Add service modules for FTP, SMTP, SNMP, LDAP, Kerberos, NFS, RPC, WinRM, MSSQL, MySQL, PostgreSQL, and Redis
- [ ] Add Linux privilege escalation checklist generator
- [ ] Add Windows privilege escalation checklist generator
- [ ] Add Active Directory lab checklist generator
- [ ] Add web app checklist generator

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
