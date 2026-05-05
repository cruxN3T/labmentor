from pathlib import Path

from typer.testing import CliRunner

from labmentor.cli import app

runner = CliRunner()


def test_status_and_services_workflow(tmp_path):
    nmap_file = tmp_path / "nmap.txt"
    nmap_file.write_text(
        """
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.9p1 Ubuntu
80/tcp open  http    Apache httpd 2.4.52
""",
        encoding="utf-8",
    )

    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(
            app,
            ["start", "--platform", "htb", "--name", "sample", "--target", "10.10.10.10"],
        )
        assert result.exit_code == 0

        result = runner.invoke(app, ["import-nmap", str(nmap_file)])
        assert result.exit_code == 0

        result = runner.invoke(app, ["status"])
        assert result.exit_code == 0
        assert "sample" in result.output
        assert "Services imported" in result.output

        result = runner.invoke(app, ["services"])
        assert result.exit_code == 0
        assert "22/tcp" in result.output
        assert "80/tcp" in result.output


def test_checklist_command_outputs_requested_checklist():
    result = runner.invoke(app, ["checklist", "--type", "ad"])
    assert result.exit_code == 0
    assert "ad Checklist" in result.output
    assert "Identify domain name" in result.output


def test_checklist_command_rejects_unknown_type():
    result = runner.invoke(app, ["checklist", "--type", "unknown"])
    assert result.exit_code == 1
    assert "Valid checklists" in result.output


def test_next_warns_about_placeholders(tmp_path):
    nmap_file = tmp_path / "ad-nmap.txt"
    nmap_file.write_text(
        """
PORT     STATE SERVICE      VERSION
88/tcp   open  kerberos-sec Microsoft Windows Kerberos
389/tcp  open  ldap         Microsoft Windows Active Directory LDAP
445/tcp  open  microsoft-ds Windows Server SMB
5985/tcp open  wsman        Microsoft HTTPAPI httpd
""",
        encoding="utf-8",
    )

    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(
            app,
            ["start", "--platform", "htb", "--name", "ad", "--target", "10.10.10.50"],
        )
        assert result.exit_code == 0

        result = runner.invoke(app, ["import-nmap", str(nmap_file)])
        assert result.exit_code == 0

        result = runner.invoke(app, ["next"])
        assert result.exit_code == 0
        assert "Replace before running" in result.output
        assert "LAB.LOCAL" in result.output
        assert "USER" in result.output
        assert "PASS" in result.output


def test_workspace_command_shows_paths(tmp_path):
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(app, ["workspace"])
        assert result.exit_code == 0
        assert "Workspace" in result.output
        assert "missing" in result.output

        result = runner.invoke(
            app,
            ["start", "--platform", "htb", "--name", "sample", "--target", "10.10.10.10"],
        )
        assert result.exit_code == 0

        result = runner.invoke(app, ["workspace"])
        assert result.exit_code == 0
        assert "State file" in result.output
        assert "exists" in result.output


def test_reset_requires_confirmation_and_deletes_workspace(tmp_path):
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(
            app,
            ["start", "--platform", "htb", "--name", "sample", "--target", "10.10.10.10"],
        )
        assert result.exit_code == 0
        assert Path(".labmentor").exists()

        result = runner.invoke(app, ["reset"])
        assert result.exit_code == 1
        assert Path(".labmentor").exists()
        assert "reset --yes" in result.output

        result = runner.invoke(app, ["reset", "--yes"])
        assert result.exit_code == 0
        assert not Path(".labmentor").exists()
