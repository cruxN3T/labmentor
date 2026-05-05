import json

from typer.testing import CliRunner

from labmentor.cli import app

runner = CliRunner()


def test_vault_set_show_and_notes_obsidian(tmp_path, monkeypatch):
    config_home = tmp_path / "config"
    vault = tmp_path / "vault"
    monkeypatch.setenv("LABMENTOR_CONFIG_HOME", str(config_home))

    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(app, ["vault", "set", str(vault)])
        assert result.exit_code == 0
        assert vault.exists()

        config_file = config_home / "config.json"
        assert config_file.exists()
        config = json.loads(config_file.read_text(encoding="utf-8"))
        assert config["vault_path"] == str(vault.resolve())

        result = runner.invoke(app, ["vault", "show"])
        assert result.exit_code == 0
        assert "Vault path" in result.output
        assert "exists" in result.output

        result = runner.invoke(
            app,
            ["start", "--platform", "offsec", "--name", "PG Sorcerer", "--target", "192.168.100.10"],
        )
        assert result.exit_code == 0

        result = runner.invoke(app, ["notes", "--obsidian"])
        assert result.exit_code == 0

        note_path = vault / "OffSec" / "PG-Sorcerer.md"
        assert note_path.exists()
        assert "PG Sorcerer" in note_path.read_text(encoding="utf-8")


def test_vault_show_fails_without_config(tmp_path, monkeypatch):
    monkeypatch.setenv("LABMENTOR_CONFIG_HOME", str(tmp_path / "config"))

    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(app, ["vault", "show"])
        assert result.exit_code == 1
        assert "No Obsidian vault configured" in result.output
