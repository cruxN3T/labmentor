from __future__ import annotations

from labmentor.models import Service


def recommend_next_steps(services: list[Service], target: str) -> list[dict[str, object]]:
    recommendations: list[dict[str, object]] = []
    names = {service.name.lower() for service in services}
    ports = {service.port for service in services}

    if has_smb(names, ports):
        recommendations.append(
            {
                "title": "Start with SMB enumeration",
                "why": "SMB often exposes shares, usernames, backups, configuration files, or credentials in labs.",
                "commands": [
                    f"smbclient -L //{target} -N",
                    f"smbmap -H {target}",
                    f"nmap --script smb-enum-shares,smb-enum-users -p445 {target}",
                ],
                "look_for": [
                    "anonymous access",
                    "readable shares",
                    "backup files",
                    "configuration files",
                    "usernames or credentials",
                    "files that map to the web root",
                ],
            }
        )

    if has_web(names, ports):
        recommendations.append(
            {
                "title": "Enumerate the web application",
                "why": "HTTP services often reveal hidden routes, admin panels, technologies, uploads, backups, or source clues.",
                "commands": [
                    f"whatweb http://{target}",
                    f"curl -i http://{target}/",
                    f"feroxbuster -u http://{target} -w /usr/share/seclists/Discovery/Web-Content/raft-small-words.txt -x php,txt,bak,zip,conf",
                ],
                "look_for": [
                    "login panels",
                    "hidden directories",
                    "backup archives",
                    "config files",
                    "upload functionality",
                    "version disclosures",
                    "interesting comments or JavaScript files",
                ],
            }
        )

    if has_ftp(names, ports):
        recommendations.append(
            {
                "title": "Check FTP access and exposed files",
                "why": "FTP may allow anonymous login or expose files that contain credentials, source code, or internal paths.",
                "commands": [
                    f"ftp {target}",
                    f"nmap --script ftp-anon,ftp-syst -p21 {target}",
                ],
                "look_for": [
                    "anonymous login",
                    "writable directories",
                    "backup files",
                    "credentials",
                    "source or deployment files",
                ],
            }
        )

    if has_ssh(names, ports):
        recommendations.append(
            {
                "title": "Save SSH for credential reuse",
                "why": "SSH is usually useful after you discover valid usernames or passwords elsewhere.",
                "commands": [f"ssh <user>@{target}"],
                "look_for": [
                    "credentials found from SMB, FTP, web files, or source code",
                    "username patterns",
                    "private keys with weak permissions",
                ],
            }
        )

    if not recommendations:
        recommendations.append(
            {
                "title": "Deepen service enumeration",
                "why": "No common high-signal service path was identified yet. Re-check full-port scans and service versions.",
                "commands": [
                    f"nmap -p- --min-rate 5000 {target}",
                    f"nmap -sC -sV -p <ports> {target}",
                ],
                "look_for": [
                    "missed ports",
                    "unusual services",
                    "version-specific clues",
                    "default credentials in authorized labs",
                ],
            }
        )

    return recommendations


def has_smb(names: set[str], ports: set[int]) -> bool:
    return bool({"microsoft-ds", "netbios-ssn", "smb"} & names) or bool({139, 445} & ports)


def has_web(names: set[str], ports: set[int]) -> bool:
    return bool({"http", "http-proxy", "https", "ssl/http"} & names) or bool({80, 443, 8080, 8000, 8443} & ports)


def has_ftp(names: set[str], ports: set[int]) -> bool:
    return "ftp" in names or 21 in ports


def has_ssh(names: set[str], ports: set[int]) -> bool:
    return "ssh" in names or 22 in ports
