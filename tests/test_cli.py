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
