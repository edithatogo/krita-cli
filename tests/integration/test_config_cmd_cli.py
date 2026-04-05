"""Integration tests for config CLI commands."""

from __future__ import annotations

from typer.testing import CliRunner

from krita_cli import config_cmd
from krita_cli.app import app

runner = CliRunner()


def test_config_show_defaults(monkeypatch, tmp_path):
    config_file = tmp_path / "config.json"
    monkeypatch.setattr(config_cmd, "CONFIG_FILE", config_file)
    monkeypatch.setattr(config_cmd, "CONFIG_DIR", tmp_path)

    result = runner.invoke(app, ["config", "show"])
    assert result.exit_code == 0
    assert "port" in result.stdout
    assert "5678" in result.stdout


def test_config_set_and_show(monkeypatch, tmp_path):
    config_file = tmp_path / "config.json"
    monkeypatch.setattr(config_cmd, "CONFIG_FILE", config_file)
    monkeypatch.setattr(config_cmd, "CONFIG_DIR", tmp_path)

    result = runner.invoke(app, ["config", "set", "port", "9999"])
    assert result.exit_code == 0
    assert "Set port = 9999" in result.stdout

    result2 = runner.invoke(app, ["config", "show"])
    assert result2.exit_code == 0
    assert "9999" in result2.stdout


def test_config_set_invalid_key(monkeypatch, tmp_path):
    config_file = tmp_path / "config.json"
    monkeypatch.setattr(config_cmd, "CONFIG_FILE", config_file)
    monkeypatch.setattr(config_cmd, "CONFIG_DIR", tmp_path)

    result = runner.invoke(app, ["config", "set", "bad_key", "value"])
    assert result.exit_code == 1
    assert "Unknown config key" in result.stdout


def test_config_reset(monkeypatch, tmp_path):
    config_file = tmp_path / "config.json"
    monkeypatch.setattr(config_cmd, "CONFIG_FILE", config_file)
    monkeypatch.setattr(config_cmd, "CONFIG_DIR", tmp_path)

    # Set a custom value
    runner.invoke(app, ["config", "set", "port", "9999"])
    # Reset
    result = runner.invoke(app, ["config", "reset"])
    assert result.exit_code == 0
    assert "reset to defaults" in result.stdout

    # Check defaults are restored
    result2 = runner.invoke(app, ["config", "show"])
    assert "5678" in result2.stdout


def test_config_set_float(monkeypatch, tmp_path):
    config_file = tmp_path / "config.json"
    monkeypatch.setattr(config_cmd, "CONFIG_FILE", config_file)
    monkeypatch.setattr(config_cmd, "CONFIG_DIR", tmp_path)

    result = runner.invoke(app, ["config", "set", "default_timeout", "45.5"])
    assert result.exit_code == 0

    config = config_cmd.load_config()
    assert config["default_timeout"] == 45.5


def test_config_set_string(monkeypatch, tmp_path):
    config_file = tmp_path / "config.json"
    monkeypatch.setattr(config_cmd, "CONFIG_FILE", config_file)
    monkeypatch.setattr(config_cmd, "CONFIG_DIR", tmp_path)

    result = runner.invoke(app, ["config", "set", "canvas_output_dir", "/tmp/output"])
    assert result.exit_code == 0

    config = config_cmd.load_config()
    assert config["canvas_output_dir"] == "/tmp/output"
