"""Unit tests for krita_cli.config_cmd."""

from __future__ import annotations

import json

import pytest

from krita_cli import config_cmd


def test_load_config_defaults(monkeypatch, tmp_path):
    config_file = tmp_path / "config.json"
    monkeypatch.setattr(config_cmd, "CONFIG_FILE", config_file)
    monkeypatch.setattr(config_cmd, "CONFIG_DIR", tmp_path)

    config = config_cmd.load_config()
    assert config == config_cmd.DEFAULTS


def test_load_config_from_file(monkeypatch, tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps({"port": 9999}))
    monkeypatch.setattr(config_cmd, "CONFIG_FILE", config_file)
    monkeypatch.setattr(config_cmd, "CONFIG_DIR", tmp_path)

    config = config_cmd.load_config()
    assert config["port"] == 9999


def test_save_config(monkeypatch, tmp_path):
    config_file = tmp_path / "config.json"
    monkeypatch.setattr(config_cmd, "CONFIG_FILE", config_file)
    monkeypatch.setattr(config_cmd, "CONFIG_DIR", tmp_path)

    config_cmd.save_config({"port": 1234})
    assert config_file.exists()
    data = json.loads(config_file.read_text())
    assert data["port"] == 1234


def test_set_key_int(monkeypatch, tmp_path):
    config_file = tmp_path / "config.json"
    monkeypatch.setattr(config_cmd, "CONFIG_FILE", config_file)
    monkeypatch.setattr(config_cmd, "CONFIG_DIR", tmp_path)

    config_cmd.set_key("port", "9999")
    config = config_cmd.load_config()
    assert config["port"] == 9999
    assert isinstance(config["port"], int)


def test_set_key_float(monkeypatch, tmp_path):
    config_file = tmp_path / "config.json"
    monkeypatch.setattr(config_cmd, "CONFIG_FILE", config_file)
    monkeypatch.setattr(config_cmd, "CONFIG_DIR", tmp_path)

    config_cmd.set_key("default_timeout", "60.5")
    config = config_cmd.load_config()
    assert config["default_timeout"] == 60.5
    assert isinstance(config["default_timeout"], float)


def test_set_key_string(monkeypatch, tmp_path):
    config_file = tmp_path / "config.json"
    monkeypatch.setattr(config_cmd, "CONFIG_FILE", config_file)
    monkeypatch.setattr(config_cmd, "CONFIG_DIR", tmp_path)

    config_cmd.set_key("canvas_output_dir", "/custom/path")
    config = config_cmd.load_config()
    assert config["canvas_output_dir"] == "/custom/path"


def test_set_key_unknown():
    with pytest.raises(ValueError, match="Unknown config key"):
        config_cmd.set_key("nonexistent", "value")


def test_reset_config(monkeypatch, tmp_path):
    config_file = tmp_path / "config.json"
    monkeypatch.setattr(config_cmd, "CONFIG_FILE", config_file)
    monkeypatch.setattr(config_cmd, "CONFIG_DIR", tmp_path)

    # Write a custom config first
    config_cmd.save_config({"port": 9999, "custom": "value"})
    # Reset
    result = config_cmd.reset_config()
    assert result == config_cmd.DEFAULTS
    config = config_cmd.load_config()
    assert config == config_cmd.DEFAULTS


def test_load_config_creates_dir(monkeypatch, tmp_path):
    config_dir = tmp_path / "nested" / "dir"
    config_file = config_dir / "config.json"
    monkeypatch.setattr(config_cmd, "CONFIG_FILE", config_file)
    monkeypatch.setattr(config_cmd, "CONFIG_DIR", config_dir)

    config_cmd.save_config({"port": 1234})
    assert config_file.exists()
