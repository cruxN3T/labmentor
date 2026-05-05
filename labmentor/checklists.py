from __future__ import annotations

CHECKLISTS: dict[str, list[str]] = {
    "web": [
        "Identify technology stack and framework clues",
        "Review response headers, cookies, and redirects",
        "Run content discovery with common extensions",
        "Check robots.txt, sitemap.xml, and exposed documentation",
        "Inspect JavaScript for endpoints, paths, and secrets",
        "Test login, reset, registration, and upload flows manually",
        "Look for backups, archives, config files, and source disclosure",
        "Try discovered credentials across allowed services",
    ],
    "linux-privesc": [
        "Identify current user, groups, hostname, kernel, and OS version",
        "Run sudo -l and review allowed commands",
        "Search for SUID/SGID binaries and unusual capabilities",
        "Review writable directories, scripts, cron jobs, and timers",
        "Check processes, services, and command-line arguments",
        "Search home, web, app, and backup directories for credentials",
        "Review PATH, environment variables, and shell history",
        "Check NFS, Docker, LXD, writable mounts, and interesting groups",
    ],
    "windows-privesc": [
        "Identify user, groups, hostname, OS version, and domain context",
        "Review privileges with whoami /priv and group memberships",
        "Check services for weak permissions or unquoted paths",
        "Review scheduled tasks, startup folders, and autoruns",
        "Search user, web, app, and backup directories for credentials",
        "Check saved credentials, PowerShell history, and config files",
        "Review writable directories in PATH and service binary locations",
        "Check WinRM, SMB, RDP, and credential reuse opportunities",
    ],
    "ad": [
        "Identify domain name, DC hostname, and naming contexts",
        "Enumerate SMB shares and anonymous access",
        "Enumerate LDAP base information and users where allowed",
        "Check password policy and lockout risk before auth testing",
        "Build a username list from LDAP, SMB, web, or naming patterns",
        "Test Kerberos user enumeration only where allowed",
        "Check AS-REP roast and Kerberoast paths where allowed",
        "Validate credentials across SMB, LDAP, WinRM, and other exposed services",
        "Map privileges, local admin access, and delegation paths after initial access",
    ],
}


def get_checklist(name: str) -> list[str]:
    normalized = name.lower().strip()
    if normalized not in CHECKLISTS:
        valid = ", ".join(sorted(CHECKLISTS))
        raise KeyError(f"Unknown checklist '{name}'. Valid checklists: {valid}")
    return CHECKLISTS[normalized]


def valid_checklists() -> list[str]:
    return sorted(CHECKLISTS)
