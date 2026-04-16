"""Unit tests to cover type safety branches and improve coverage."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from krita_cli.app import app
from krita_client import KritaError
from krita_mcp import server as server_mod


def test_server_health_error() -> None:
    """Test krita_health with generic KritaError."""
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.health.side_effect = KritaError("generic error", code="ERR")
        mock_get.return_value = mock_client

        result = server_mod.krita_health()
        assert "[ERR] generic error" in result


def test_server_tools_error_coverage() -> None:
    """Cover error paths for all tools in server.py."""
    tools = [
        (server_mod.krita_new_canvas, {}),
        (server_mod.krita_set_color, {"color": "#000"}),
        (server_mod.krita_set_brush, {}),
        (server_mod.krita_stroke, {"points": [[0, 0]]}),
        (server_mod.krita_fill, {"x": 0, "y": 0}),
        (server_mod.krita_draw_shape, {"shape": "line", "x": 0, "y": 0}),
        (server_mod.krita_get_canvas, {}),
        (server_mod.krita_undo, {}),
        (server_mod.krita_redo, {}),
        (server_mod.krita_clear, {}),
        (server_mod.krita_save, {"path": "test.png"}),
        (server_mod.krita_get_color_at, {"x": 0, "y": 0}),
        (server_mod.krita_list_brushes, {}),
        (server_mod.krita_open_file, {"path": "test.kra"}),
        (server_mod.krita_batch, {"commands": []}),
        (server_mod.krita_rollback, {"batch_id": "123"}),
        (server_mod.krita_get_command_history, {}),
        (server_mod.krita_get_canvas_info, {}),
        (server_mod.krita_get_current_color, {}),
        (server_mod.krita_get_current_brush, {}),
        (server_mod.krita_select_rect, {"x": 0, "y": 0, "width": 1, "height": 1}),
        (server_mod.krita_select_ellipse, {"cx": 0, "cy": 0, "rx": 1, "ry": 1}),
        (server_mod.krita_select_polygon, {"points": [[0, 0]]}),
        (server_mod.krita_selection_info, {}),
        (server_mod.krita_clear_selection, {}),
        (server_mod.krita_invert_selection, {}),
        (server_mod.krita_fill_selection, {}),
        (server_mod.krita_deselect, {}),
        (server_mod.krita_select_by_color, {}),
        (server_mod.krita_select_by_alpha, {}),
        (server_mod.krita_get_capabilities, {}),
        (server_mod.krita_transform_selection, {}),
        (server_mod.krita_grow_selection, {"pixels": 1}),
        (server_mod.krita_shrink_selection, {"pixels": 1}),
        (server_mod.krita_border_selection, {"pixels": 1}),
        (server_mod.krita_save_selection, {"path": "mask.png"}),
        (server_mod.krita_load_selection, {"path": "mask.png"}),
        (server_mod.krita_selection_stats, {}),
        (server_mod.krita_save_selection_channel, {"name": "ch"}),
        (server_mod.krita_load_selection_channel, {"name": "ch"}),
        (server_mod.krita_list_selection_channels, {}),
        (server_mod.krita_security_status, {}),
    ]

    mapping = {
        "batch": "batch_execute",
        "save_selection_channel": "save_selection_channel",
        "load_selection_channel": "load_selection_channel",
        "list_selection_channels": "list_selection_channels",
        "security_status": "get_security_status",
        "selection_stats": "selection_stats",
        "capabilities": "get_capabilities",
    }

    for tool_func, kwargs in tools:
        with patch("krita_mcp.server._get_client") as mock_get:
            mock_client = MagicMock()

            base_name = tool_func.__name__.replace("krita_", "")
            method_name = mapping.get(base_name, base_name)

            # Case 1: result contains "error"
            getattr(mock_client, method_name).return_value = {"error": "tool fail"}
            mock_get.return_value = mock_client

            result = tool_func(**kwargs)
            assert "tool fail" in result

            # Case 2: KritaError raised
            getattr(mock_client, method_name).side_effect = KritaError("exc fail")
            result = tool_func(**kwargs)
            assert "exc fail" in result


def test_server_batch_type_safety_extended() -> None:
    """Test krita_batch with complex invalid results format."""
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = MagicMock()
        mock_get.return_value = mock_client

        # Test error details loop fully
        mock_client.batch_execute.return_value = {
            "results": [
                {"status": "error", "action": "a1", "error": "err1"},
                {"status": "error", "action": "a2", "result": {"error": {"message": "err2"}}},
                {"status": "error", "action": "a3", "result": {"error": "err3"}},
                {"status": "error", "action": "a4"},  # unknown err_msg
                "not a dict",
            ],
            "status": "error",
        }
        result = server_mod.krita_batch([{"action": "test"}])
        assert "a1: err1" in result
        assert "a2: err2" in result
        assert "a3: err3" in result
        assert "a4: unknown" in result


def test_cli_replay_array_check() -> None:
    """Test CLI replay check for JSON array."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        f = "not_array.json"
        with open(f, "w") as j:
            json.dump({"not": "an array"}, j)

        result = runner.invoke(app, ["replay", f])
        assert "JSON file must contain an array" in result.output


def test_cli_history_empty_check() -> None:
    """Test CLI history check for no records."""
    with patch("krita_cli._shared._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.get_command_history.return_value = {"history": []}
        mock_get.return_value = mock_client

        runner = CliRunner()
        result = runner.invoke(app, ["history"])
        assert "No command history recorded" in result.output


def test_cli_history_with_error_check() -> None:
    """Test CLI history check for records with errors."""
    with patch("krita_cli._shared._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.get_command_history.return_value = {
            "history": [{"action": "test", "status": "error", "error": "fail", "duration_ms": 10}]
        }
        mock_get.return_value = mock_client

        runner = CliRunner()
        result = runner.invoke(app, ["history"])
        assert "fail" in result.output


def test_cli_rollback_error_path() -> None:
    """Test CLI rollback error handling."""
    with patch("krita_cli._shared._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.rollback.side_effect = KritaError("rollback fail")
        mock_get.return_value = mock_client

        runner = CliRunner()
        result = runner.invoke(app, ["rollback", "123"])
        assert "rollback fail" in result.output

    with patch("krita_cli._shared._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.rollback.return_value = {"message": "done"}
        mock_get.return_value = mock_client
        runner = CliRunner()
        result = runner.invoke(app, ["rollback", "123"])
        assert "done" in result.output


def test_server_rollback_fallback() -> None:
    """Test krita_rollback message fallback."""
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.rollback.return_value = {}  # no message
        mock_get.return_value = mock_client

        result = server_mod.krita_rollback("123")
        assert "Rollback successful" in result
