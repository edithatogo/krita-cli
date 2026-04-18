"""Krita UI driver for end-to-end testing.

Handles launching Krita, opening a canvas, waiting for the MCP plugin
server to come up, and tearing down cleanly.

Requires:
  - Krita installed (auto-discovered via scoop or PATH)
  - pywinauto (pip install pywinauto)
  - The kritamcp plugin installed in %APPDATA%/krita/pykrita/
"""

from __future__ import annotations

import os
import shutil
import subprocess
import time
from pathlib import Path

import httpx


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

def _config_port() -> int:
    """Read port from ~/.krita-cli/config.json if present, else default 5678."""
    import json as _json

    for candidate in [
        Path.home() / ".krita-cli" / "config.json",
        Path.home() / ".kritamcp_config.json",
    ]:
        if candidate.exists():
            try:
                return int(_json.loads(candidate.read_text()).get("port", 5678))
            except Exception:
                pass
    return 5678


PLUGIN_PORT = _config_port()
KRITA_STARTUP_TIMEOUT = 60  # seconds to wait for Krita window
PLUGIN_STARTUP_TIMEOUT = 30  # seconds to wait for plugin HTTP server
PLUGIN_SRC = Path(__file__).parent.parent.parent / "krita-plugin"
PYKRITA_DIR = Path(os.environ.get("APPDATA", "~")) / "krita" / "pykrita"
STARTUP_LOG = Path.home() / "kritamcp_startup.log"
DIAG_LOG = Path.home() / "kritamcp_diag.log"


def find_krita_exe() -> Path | None:
    """Locate krita.exe via scoop, PATH, or common install locations."""
    # Try scoop
    scoop_path = Path.home() / "scoop" / "apps" / "krita" / "current" / "bin" / "krita.exe"
    if scoop_path.exists():
        return scoop_path
    # Try PATH
    from_path = shutil.which("krita")
    if from_path:
        return Path(from_path)
    # Common Windows install paths
    for candidate in [
        Path("C:/Program Files/Krita (x64)/bin/krita.exe"),
        Path("C:/Program Files/Krita/bin/krita.exe"),
    ]:
        if candidate.exists():
            return candidate
    return None


def install_plugin() -> None:
    """Copy the kritamcp plugin into Krita's pykrita directory.

    Skips files that are locked (e.g. held open by a running Krita process).
    """
    PYKRITA_DIR.mkdir(parents=True, exist_ok=True)

    desktop_src = PLUGIN_SRC / "kritamcp.desktop"
    desktop_dst = PYKRITA_DIR / "kritamcp.desktop"
    try:
        shutil.copy2(desktop_src, desktop_dst)
    except PermissionError:
        pass  # Krita has the file locked — already installed, skip

    plugin_src = PLUGIN_SRC / "kritamcp"
    plugin_dst = PYKRITA_DIR / "kritamcp"
    if not plugin_dst.exists():
        shutil.copytree(plugin_src, plugin_dst)
    else:
        # Update individual files, skipping any that are locked
        for src_file in plugin_src.rglob("*"):
            if src_file.is_file():
                rel = src_file.relative_to(plugin_src)
                dst_file = plugin_dst / rel
                dst_file.parent.mkdir(parents=True, exist_ok=True)
                try:
                    shutil.copy2(src_file, dst_file)
                except PermissionError:
                    pass  # Locked by Krita — already present, skip


def _plugin_state_summary() -> str:
    """Summarize the local plugin install and diagnostic artifacts."""
    desktop_dst = PYKRITA_DIR / "kritamcp.desktop"
    plugin_dst = PYKRITA_DIR / "kritamcp"
    diag_script = PYKRITA_DIR / "kritamcp_diag.py"
    parts = [
        f"plugin dir: {PYKRITA_DIR}",
        f"desktop present: {desktop_dst.exists()}",
        f"package present: {plugin_dst.exists()}",
        f"diagnostic script present: {diag_script.exists()}",
        f"startup log present: {STARTUP_LOG.exists()}",
        f"diagnostic log present: {DIAG_LOG.exists()}",
    ]
    return "\n".join(parts)


def wait_for_window(title_fragment: str, timeout: float = KRITA_STARTUP_TIMEOUT) -> bool:
    """Wait until a visible window with the given title fragment appears."""
    try:
        import win32gui

        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            found = []

            def _cb(hwnd: int, _: object) -> None:
                if win32gui.IsWindowVisible(hwnd) and title_fragment in win32gui.GetWindowText(hwnd):
                    found.append(hwnd)

            win32gui.EnumWindows(_cb, None)
            if found:
                return True
            time.sleep(1)
        return False
    except ImportError:
        # Not on Windows — just sleep and hope
        time.sleep(10)
        return True


def open_new_document() -> None:
    """Send Ctrl+N then Enter to open a new document with default settings."""
    try:
        import win32con
        import win32gui

        # Find and focus the Krita main window
        hwnd = None

        def _cb(h: int, _: object) -> None:
            nonlocal hwnd
            if win32gui.IsWindowVisible(h) and "Krita" in win32gui.GetWindowText(h):
                hwnd = h

        win32gui.EnumWindows(_cb, None)
        if hwnd:
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.BringWindowToTop(hwnd)
    except Exception:
        pass

    time.sleep(1)

    try:
        from pywinauto.keyboard import send_keys

        send_keys("^n")  # Ctrl+N — New document dialog
        time.sleep(3)    # Wait for dialog to appear
        send_keys("{ENTER}")  # Accept defaults
        time.sleep(2)    # Wait for canvas to open
    except Exception:
        pass


def wait_for_plugin(timeout: float = PLUGIN_STARTUP_TIMEOUT) -> bool:
    """Poll the configured /health endpoint until the plugin responds or timeout."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            r = httpx.get(f"http://127.0.0.1:{PLUGIN_PORT}/health", timeout=2)
            if r.json().get("status") == "ok":
                return True
        except Exception:
            pass
        time.sleep(1)
    return False


class KritaDriver:
    """Context manager that owns a Krita subprocess for the duration of a test session."""

    def __init__(self) -> None:
        self._proc: subprocess.Popen[bytes] | None = None
        self._owned = False  # True if we launched Krita ourselves

    def start(self) -> None:
        """Install plugin, launch Krita, open a canvas, wait for plugin server."""
        # If plugin already responding, nothing to do
        try:
            r = httpx.get(f"http://127.0.0.1:{PLUGIN_PORT}/health", timeout=2)
            if r.json().get("status") == "ok":
                return  # Already running
        except Exception:
            pass

        exe = find_krita_exe()
        if exe is None:
            raise RuntimeError("Krita executable not found. Install Krita or add it to PATH.")

        install_plugin()

        env = {k: v for k, v in os.environ.items() if k != "SSL_CERT_FILE"}
        self._proc = subprocess.Popen(
            [str(exe)],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self._owned = True

        if not wait_for_window("Krita", timeout=KRITA_STARTUP_TIMEOUT):
            stdout = self._read_output()
            self.stop()
            raise RuntimeError(
                f"Krita window did not appear within {KRITA_STARTUP_TIMEOUT}s.\n"
                f"Krita output:\n{stdout}"
            )

        # Wait for Krita to finish its splash/loading sequence
        time.sleep(4)
        open_new_document()
        # Give createActions time to fire and the server thread to bind
        time.sleep(3)

        if not wait_for_plugin(timeout=PLUGIN_STARTUP_TIMEOUT):
            stdout = self._read_output()
            state = _plugin_state_summary()
            if not STARTUP_LOG.exists() and (PYKRITA_DIR / "kritamcp.desktop").exists():
                cause = (
                    "Krita launched, but the plugin startup log never appeared. "
                    "That usually means the plugin is installed but disabled in Krita's "
                    "Python Plugin Manager, or Krita skipped loading it at startup."
                )
            elif STARTUP_LOG.exists() and not DIAG_LOG.exists():
                cause = (
                    "Krita launched and the plugin appears to have loaded, but the HTTP "
                    "server did not bind. That usually indicates a startup/import failure "
                    "inside the plugin."
                )
            else:
                cause = (
                    "Krita launched, but the plugin health endpoint never responded. "
                    "Check for a port/config mismatch or a startup failure."
                )
            self.stop()
            raise RuntimeError(
                f"Krita MCP plugin did not start on port {PLUGIN_PORT} within "
                f"{PLUGIN_STARTUP_TIMEOUT}s.\n"
                f"{cause}\n"
                "If the plugin files are present, enable 'Krita MCP Bridge' in:\n"
                "  Settings → Configure Krita → Python Plugin Manager\n"
                "Then restart Krita and try again.\n"
                f"{state}\n"
                f"Krita output:\n{stdout}"
            )

    def _read_output(self) -> str:
        """Read any available output from the Krita process without blocking."""
        if self._proc is None or self._proc.stdout is None:
            return "(no output)"
        try:
            # Non-blocking read on Windows via a short timeout thread
            import threading

            buf: list[bytes] = []

            def _reader() -> None:
                try:
                    buf.append(self._proc.stdout.read(8192))  # type: ignore[union-attr]
                except Exception:
                    pass

            t = threading.Thread(target=_reader, daemon=True)
            t.start()
            t.join(timeout=2)
            if buf:
                return buf[0].decode(errors="replace")
        except Exception:
            pass
        return "(unavailable)"

    def stop(self) -> None:
        if self._owned and self._proc is not None:
            self._proc.terminate()
            try:
                self._proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self._proc.kill()
            self._proc = None

    def __enter__(self) -> KritaDriver:
        self.start()
        return self

    def __exit__(self, *_: object) -> None:
        self.stop()
