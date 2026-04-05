"""Integration tests for the 'krita config' CLI command."""

from __future__ import annotations

import pytest
from typer.testing import CliRunner

from krita_cli import config_cmd
from krita_cli.app import app

runner = CliRunner()


@pytest.fixture
def mock_config(tmp_path, monkeypatch):
    config_dir = tmp_path / ".krita-cli"
    config_file = config_dir / "config.json"
    monkeypatch.setattr(config_cmd, "CONFIG_DIR", config_dir)
    monkeypatch.setattr(config_cmd, "CONFIG_FILE", config_file)
    return config_file


def test_config_show_defaults(mock_config):
    result = runner.invoke(app, ["config", "show"])
    assert result.exit_code == 0
    # Should show default port
    assert "port" in result.stdout
    assert "5678" in result.stdout


def test_config_set_and_show(mock_config):
    result = runner.invoke(app, ["config", "set", "port", "1234"])
    assert result.exit_code == 0
    assert "Set port = 1234" in result.stdout

    result = runner.invoke(app, ["config", "show"])
    assert result.exit_code == 0
    assert "1234" in result.stdout


def test_config_reset(mock_config):
    runner.invoke(app, ["config", "set", "port", "1234"])
    result = runner.invoke(app, ["config", "reset"])
    assert result.exit_code == 0
    assert "reset to defaults" in result.stdout

    result = runner.invoke(app, ["config", "show"])
    assert "5678" in result.stdout


def test_config_set_invalid_key(mock_config):
    result = runner.invoke(app, ["config", "set", "invalid_key", "value"])
    assert result.exit_code == 1
    assert "Unknown config key" in result.stdout
