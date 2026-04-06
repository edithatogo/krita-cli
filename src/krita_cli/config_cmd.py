"""Plugin configuration management.

Provides functions to load, save, and modify plugin configuration stored in
``~/.krita-cli/config.json``.  The plugin reads this file on startup so that
CLI changes persist across Krita restarts.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

CONFIG_DIR = Path.home() / ".krita-cli"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULTS: dict[str, Any] = {
    "port": 5678,
    "canvas_output_dir": "~/krita-mcp-output",
    "default_timeout": 30.0,
    "export_timeout": 120.0,
    "max_canvas_dim": 8192,
    "max_batch_size": 50,
    "max_layers": 100,
    "max_commands_per_minute": 60,
}


def load_config() -> dict[str, Any]:
    """Load plugin configuration from disk, falling back to defaults."""
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            # Config file is corrupted; fall back to defaults
            return dict(DEFAULTS)
    return dict(DEFAULTS)


def save_config(config: dict[str, Any]) -> None:
    """Persist *config* to disk, creating the config directory if needed."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(config, indent=2), encoding="utf-8")


def set_key(key: str, value: str) -> None:
    """Set a single configuration *key* to *value* with type coercion.

    Raises ``ValueError`` if *key* is not recognised.
    """
    if key not in DEFAULTS:
        raise ValueError(f"Unknown config key: {key}")
    config = load_config()
    default = DEFAULTS[key]
    if isinstance(default, int):
        config[key] = int(value)
    elif isinstance(default, float):
        config[key] = float(value)
    else:
        config[key] = value
    save_config(config)


def reset_config() -> dict[str, Any]:
    """Reset configuration to defaults and persist them."""
    defaults = dict(DEFAULTS)
    save_config(defaults)
    return defaults
