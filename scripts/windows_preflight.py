"""Windows preflight checks for Krita MCP.

This script is intentionally stdlib-only so it can diagnose a broken project
runtime before pytest or the CLI imports any third-party dependencies.
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import shutil
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"
PLUGIN_DIR = ROOT / "krita-plugin"
for candidate in (SRC_DIR, PLUGIN_DIR):
    path = str(candidate)
    if path not in sys.path:
        sys.path.insert(0, path)


def _check_native_imports(errors: list[str]) -> None:
    try:
        import ssl  # noqa: F401
        import ctypes  # noqa: F401
    except Exception as exc:  # pragma: no cover - platform/runtime specific
        errors.append(f"native runtime imports failed: {exc}")


def _check_project_imports(errors: list[str]) -> None:
    for module_name in ("krita_cli", "krita_client", "krita_mcp", "kritamcp"):
        if importlib.util.find_spec(module_name) is None:
            errors.append(f"module not importable: {module_name}")


def _check_krita_install(errors: list[str]) -> None:
    if shutil.which("krita") is not None:
        return

    candidates = [
        Path.home() / "scoop" / "apps" / "krita" / "current" / "bin" / "krita.exe",
        Path("C:/Program Files/Krita (x64)/bin/krita.exe"),
        Path("C:/Program Files/Krita/bin/krita.exe"),
    ]
    if not any(candidate.exists() for candidate in candidates):
        errors.append("krita.exe not found via PATH, scoop, or Program Files")


def _check_plugin_files(errors: list[str]) -> None:
    appdata = os.environ.get("APPDATA")
    if not appdata:
        errors.append("APPDATA is not set")
        return

    plugin_root = Path(appdata) / "krita" / "pykrita"
    desktop_file = plugin_root / "kritamcp.desktop"
    package_root = plugin_root / "kritamcp"
    startup_script = plugin_root / "kritamcp_diag.py"

    if not plugin_root.exists():
        errors.append(f"plugin directory missing: {plugin_root}")
        return

    if not desktop_file.exists():
        errors.append(f"plugin desktop file missing: {desktop_file}")
    if not package_root.exists():
        errors.append(f"plugin package missing: {package_root}")
    if not startup_script.exists():
        errors.append(f"diagnostic script missing: {startup_script}")


def _check_live_health(errors: list[str], timeout: float) -> None:
    config_port = 5678
    for candidate in [
        Path.home() / ".krita-cli" / "config.json",
        Path.home() / ".kritamcp_config.json",
    ]:
        if candidate.exists():
            try:
                import json

                config_port = int(json.loads(candidate.read_text()).get("port", 5678))
                break
            except Exception:
                pass

    url = f"http://127.0.0.1:{config_port}/health"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            if response.status != 200:
                errors.append(f"health endpoint returned HTTP {response.status} at {url}")
    except Exception as exc:  # pragma: no cover - depends on local Krita state
        errors.append(f"health endpoint unavailable at {url}: {exc}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Windows Krita MCP preflight")
    parser.add_argument("--check-live", action="store_true", help="probe the local health endpoint")
    parser.add_argument("--health-timeout", type=float, default=2.0, help="health check timeout in seconds")
    args = parser.parse_args()

    errors: list[str] = []
    _check_native_imports(errors)
    _check_project_imports(errors)
    _check_krita_install(errors)
    _check_plugin_files(errors)
    if args.check_live:
        _check_live_health(errors, args.health_timeout)

    if errors:
        print("Windows Krita MCP preflight failed:")
        for item in errors:
            print(f"- {item}")
        return 1

    print("Windows Krita MCP preflight passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
