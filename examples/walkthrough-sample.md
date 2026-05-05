# Example Walkthrough

The target exposes SSH, HTTP, and SMB.

Start with SMB enumeration:

```bash
smbclient -L //10.10.10.10 -N
smbmap -H 10.10.10.10
```

A readable share contains `backup.zip`. Download it and inspect the archive. The backup contains web application source code and a database config file with credentials.

Reuse the credentials over SSH:

```bash
ssh dev@10.10.10.10
```

After initial access, run privilege escalation enumeration:

```bash
sudo -l
find / -perm -4000 -type f 2>/dev/null
```

A SUID helper binary can be abused to read root-owned files.
