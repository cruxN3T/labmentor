from __future__ import annotations

from labmentor.models import Service


def recommend_next_steps(services: list[Service], target: str) -> list[dict[str, object]]:
    recommendations: list[dict[str, object]] = []
    names = {service.name.lower() for service in services}
    ports = {service.port for service in services}

    if has_ad_services(names, ports):
        recommendations.append(
            {
                "title": "Enumerate likely Windows or Active Directory services",
                "why": "Kerberos, LDAP, SMB, and WinRM together often indicate a Windows or Active Directory lab path. Focus on domain discovery, user enumeration, shares, and credential reuse.",
                "commands": [
                    f"nmap -sC -sV -p88,135,139,389,445,464,593,636,3268,3269,5985,5986 {target}",
                    f"enum4linux-ng {target}",
                    f"crackmapexec smb {target}",
                    f"ldapsearch -x -H ldap://{target} -s base namingcontexts",
                    f"kerbrute userenum --dc {target} -d LAB.LOCAL users.txt  # replace LAB.LOCAL and users.txt",
                    f"evil-winrm -i {target} -u USER -p PASS  # replace USER and PASS after creds are found",
                ],
                "look_for": [
                    "domain name and naming contexts",
                    "anonymous LDAP or SMB information",
                    "valid usernames",
                    "readable SMB shares",
                    "password policy and lockout risk",
                    "credentials that can be reused over SMB or WinRM",
                    "Kerberos user enumeration or AS-REP roasting opportunities where allowed",
                ],
            }
        )

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

    if has_nfs(names, ports):
        recommendations.append(
            {
                "title": "Enumerate NFS exports",
                "why": "NFS can expose mounted directories, backups, home folders, web roots, or files that can be mounted locally for deeper review.",
                "commands": [
                    f"showmount -e {target}",
                    f"nmap --script nfs-showmount,nfs-ls,nfs-statfs -p111,2049 {target}",
                    f"mkdir -p mnt/nfs && sudo mount -t nfs {target}:/<export> mnt/nfs -o nolock  # replace <export>",
                ],
                "look_for": [
                    "world-readable exports",
                    "home directories",
                    "web application files",
                    "backup archives",
                    "SSH keys",
                    "UID/GID permission issues",
                    "files writable after mounting",
                ],
            }
        )

    if has_snmp(names, ports):
        recommendations.append(
            {
                "title": "Enumerate SNMP information",
                "why": "SNMP can leak usernames, running processes, network interfaces, installed software, hostnames, and sometimes sensitive command arguments.",
                "commands": [
                    f"snmpwalk -v2c -c public {target}",
                    f"onesixtyone -c /usr/share/seclists/Discovery/SNMP/snmp.txt {target}",
                    f"snmpwalk -v2c -c public {target} 1.3.6.1.2.1.25.4.2.1.2",
                    f"snmpwalk -v2c -c public {target} 1.3.6.1.4.1.77.1.2.25",
                ],
                "look_for": [
                    "valid community strings",
                    "local usernames",
                    "running processes",
                    "software versions",
                    "network interfaces",
                    "mounted paths",
                    "credentials in process arguments",
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
                "commands": [f"ssh <user>@{target}  # replace <user> after creds are found"],
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
                    f"nmap -sC -sV -p <ports> {target}  # replace <ports>",
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


def has_ad_services(names: set[str], ports: set[int]) -> bool:
    ad_names = {"kerberos", "kerberos-sec", "ldap", "ldaps", "microsoft-ds", "ms-wbt-server", "wsman"}
    ad_ports = {88, 389, 445, 464, 593, 636, 3268, 3269, 5985, 5986}
    return bool(ad_names & names) or len(ad_ports & ports) >= 2 or bool({5985, 5986} & ports)


def has_smb(names: set[str], ports: set[int]) -> bool:
    return bool({"microsoft-ds", "netbios-ssn", "smb"} & names) or bool({139, 445} & ports)


def has_nfs(names: set[str], ports: set[int]) -> bool:
    return bool({"nfs", "mountd", "rpcbind"} & names) or bool({111, 2049} & ports)


def has_snmp(names: set[str], ports: set[int]) -> bool:
    return "snmp" in names or 161 in ports


def has_web(names: set[str], ports: set[int]) -> bool:
    return bool({"http", "http-proxy", "https", "ssl/http"} & names) or bool({80, 443, 8080, 8000, 8443} & ports)


def has_ftp(names: set[str], ports: set[int]) -> bool:
    return "ftp" in names or 21 in ports


def has_ssh(names: set[str], ports: set[int]) -> bool:
    return "ssh" in names or 22 in ports
