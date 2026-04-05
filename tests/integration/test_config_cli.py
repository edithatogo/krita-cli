"""Tests for config_cli commands."""

import json
from pathlib import Path
from typer.testing import CliRunner

from krita_cli.cli import app
from krita_cli import config_cli

runner = CliRunner()


def test_config_show_empty(monkeypatch, tmp_path):
    config_path = tmp_path / "kritamcp_config.json"
    monkeypatch.setattr(config_cli, "CONFIG_PATH", str(config_path))
    
    result = runner.invoke(app, ["config", "show"])
    assert result.exit_code == 0
    assert "(No config stored)" in result.stdout


def test_config_set_and_show(monkeypatch, tmp_path):
    config_path = tmp_path / "kritamcp_config.json"
    monkeypatch.setattr(config_cli, "CONFIG_PATH", str(config_path))
    
    result = runner.invoke(app, ["config", "set", "port", "1234"])
    assert result.exit_code == 0
    assert "Successfully set" in result.stdout
    assert "1234" in result.stdout
    
    with open(config_path, "r") as f:
        data = json.loads(f.read())
        assert data["port"] == 1234
    
    result2 = runner.invoke(app, ["config", "show"])
    assert result2.exit_code == 0
    assert "port" in result2.stdout
    assert "1234" in result2.stdout

def test_config_set_bool(monkeypatch, tmp_path):
    config_path = tmp_path / "kritamcp_config.json"
    monkeypatch.setattr(config_cli, "CONFIG_PATH", str(config_path))
    
    result = runner.invoke(app, ["config", "set", "some_flag", "true"])
    assert result.exit_code == 0
    
    with open(config_path, "r") as f:
        data = json.loads(f.read())
        assert data["some_flag"] is True

def test_config_read_error(monkeypatch, tmp_path):
    config_path = tmp_path / "kritamcp_config.json"
    config_path.write_text("{invalid json]")
    monkeypatch.setattr(config_cli, "CONFIG_PATH", str(config_path))
    
    result = runner.invoke(app, ["config", "show"])
    assert result.exit_code == 0
    assert "Error reading config" in result.stdout

def test_config_write_error(monkeypatch):
    monkeypatch.setattr(config_cli, "CONFIG_PATH", "/this/path/does/not/exist/config.json")
    
    result = runner.invoke(app, ["config", "set", "a", "b"])
    assert result.exit_code == 0
    assert "Error writing config" in result.stdout
