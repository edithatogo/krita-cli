#!/usr/bin/env python
"""Export a Krita API inventory from local stubs and, optionally, a live Krita runtime.

The script is deliberately standard-library only so it can run:

1. In a normal dev shell, where it will always be able to inventory the local
   `types/krita/__init__.pyi` surface.
2. Inside Krita's embedded Python, where `import krita` works and the script
   can also inspect live module members plus the currently active objects.

Examples:

    python scripts/export_krita_api_inventory.py
    python scripts/export_krita_api_inventory.py --source stubs --output krita-api-stubs.json
    python scripts/export_krita_api_inventory.py --source runtime --output krita-api-runtime.json
"""

from __future__ import annotations

import argparse
import ast
import inspect
import json
import platform
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
STUB_PATH = ROOT / "types" / "krita" / "__init__.pyi"
DEFAULT_RUNTIME_CLASSES = (
    "InfoObject",
    "ManagedColor",
    "Canvas",
    "Action",
    "Node",
    "Document",
    "View",
    "Window",
    "Resource",
    "Extension",
    "Krita",
)


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def _safe_signature(obj: Any) -> str | None:
    try:
        return str(inspect.signature(obj))
    except (TypeError, ValueError):
        return None


def _inspect_namespace_members(namespace: Any) -> dict[str, list[dict[str, Any]]]:
    methods: list[dict[str, Any]] = []
    attributes: list[dict[str, Any]] = []

    for name in sorted(dir(namespace)):
        if name.startswith("_"):
            continue
        try:
            member = getattr(namespace, name)
        except Exception as exc:  # noqa: BLE001 # pragma: no cover - defensive against Qt wrappers
            attributes.append(
                {
                    "name": name,
                    "kind": "unreadable",
                    "detail": f"{type(exc).__name__}: {exc}",
                }
            )
            continue

        if callable(member):
            methods.append(
                {
                    "name": name,
                    "signature": _safe_signature(member),
                    "owner": getattr(getattr(member, "__qualname__", None), "split", lambda *_: [])(".")[0]
                    if hasattr(member, "__qualname__")
                    else None,
                }
            )
        else:
            attributes.append({"name": name, "type": type(member).__name__})

    return {"methods": methods, "attributes": attributes}


def _stub_method_signature(node: ast.FunctionDef) -> str:
    positional = [arg.arg for arg in node.args.posonlyargs + node.args.args]
    vararg = f"*{node.args.vararg.arg}" if node.args.vararg else None
    kwonly = [arg.arg for arg in node.args.kwonlyargs]
    kwarg = f"**{node.args.kwarg.arg}" if node.args.kwarg else None

    parts = positional[:]
    if node.args.kwonlyargs and not node.args.vararg:
        parts.append("*")
    if vararg:
        parts.append(vararg)
    parts.extend(kwonly)
    if kwarg:
        parts.append(kwarg)
    return f"({', '.join(parts)})"


def load_stub_inventory(stub_path: Path) -> dict[str, Any]:
    source = stub_path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(stub_path))

    module_functions: list[dict[str, Any]] = []
    classes: dict[str, dict[str, Any]] = {}

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            methods = []
            for child in node.body:
                if isinstance(child, ast.FunctionDef):
                    methods.append(
                        {
                            "name": child.name,
                            "signature": _stub_method_signature(child),
                        }
                    )
            classes[node.name] = {
                "docstring": ast.get_docstring(node),
                "method_count": len(methods),
                "methods": methods,
            }
        elif isinstance(node, ast.FunctionDef):
            module_functions.append(
                {
                    "name": node.name,
                    "signature": _stub_method_signature(node),
                }
            )

    return {
        "available": True,
        "path": str(stub_path),
        "module_function_count": len(module_functions),
        "class_count": len(classes),
        "module_functions": module_functions,
        "classes": classes,
    }


def load_runtime_inventory() -> dict[str, Any]:  # noqa: PLR0912
    try:
        import krita as krita_module  # type: ignore[import-not-found]  # noqa: PLC0415
    except Exception as exc:  # noqa: BLE001 # pragma: no cover - depends on Krita runtime
        return {
            "available": False,
            "import_error": f"{type(exc).__name__}: {exc}",
        }

    runtime: dict[str, Any] = {
        "available": True,
        "module": _inspect_namespace_members(krita_module),
        "classes": {},
        "live_objects": {},
    }

    for class_name in DEFAULT_RUNTIME_CLASSES:
        cls = getattr(krita_module, class_name, None)
        if cls is None:
            continue
        runtime["classes"][class_name] = _inspect_namespace_members(cls)

    krita_cls = getattr(krita_module, "Krita", None)
    if krita_cls is None:
        return runtime

    try:
        krita_instance = krita_cls.instance()
    except Exception as exc:  # noqa: BLE001 # pragma: no cover - depends on Krita runtime
        runtime["live_objects"]["krita_instance"] = {
            "available": False,
            "error": f"{type(exc).__name__}: {exc}",
        }
        return runtime

    if krita_instance is None:
        runtime["live_objects"]["krita_instance"] = {"available": False, "error": "Krita.instance() returned None"}
        return runtime

    runtime["live_objects"]["krita_instance"] = {
        "available": True,
        "type": type(krita_instance).__name__,
        **_inspect_namespace_members(krita_instance),
    }

    def add_live_object(name: str, obj: Any) -> None:
        if obj is None:
            runtime["live_objects"][name] = {"available": False}
            return
        runtime["live_objects"][name] = {
            "available": True,
            "type": type(obj).__name__,
            **_inspect_namespace_members(obj),
        }

    try:
        window = krita_instance.activeWindow()
    except Exception as exc:  # noqa: BLE001 # pragma: no cover - depends on Krita runtime
        runtime["live_objects"]["active_window"] = {
            "available": False,
            "error": f"{type(exc).__name__}: {exc}",
        }
        return runtime

    add_live_object("active_window", window)

    document = None
    if window is not None:
        try:
            document = window.activeDocument()
        except Exception as exc:  # noqa: BLE001 # pragma: no cover - depends on Krita runtime
            runtime["live_objects"]["active_document"] = {
                "available": False,
                "error": f"{type(exc).__name__}: {exc}",
            }
        else:
            add_live_object("active_document", document)

        try:
            view = window.activeView()
        except Exception as exc:  # noqa: BLE001 # pragma: no cover - depends on Krita runtime
            runtime["live_objects"]["active_view"] = {
                "available": False,
                "error": f"{type(exc).__name__}: {exc}",
            }
        else:
            add_live_object("active_view", view)
    else:
        runtime["live_objects"]["active_document"] = {"available": False}
        runtime["live_objects"]["active_view"] = {"available": False}

    if document is not None:
        try:
            add_live_object("active_layer", document.activeNode())
        except Exception as exc:  # noqa: BLE001 # pragma: no cover - depends on Krita runtime
            runtime["live_objects"]["active_layer"] = {
                "available": False,
                "error": f"{type(exc).__name__}: {exc}",
            }
    else:
        runtime["live_objects"]["active_layer"] = {"available": False}

    return runtime


def build_inventory(source: str) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "generated_at": _now_iso(),
        "repo_root": str(ROOT),
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "source": source,
    }

    if source in {"stubs", "both"}:
        payload["stubs"] = load_stub_inventory(STUB_PATH)
    if source in {"runtime", "both"}:
        payload["runtime"] = load_runtime_inventory()

    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        choices=("stubs", "runtime", "both"),
        default="both",
        help="Choose which inventory source to export.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional output path. Defaults to stdout.",
    )
    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="JSON indentation level.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_inventory(args.source)
    rendered = json.dumps(payload, indent=args.indent, sort_keys=True)

    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        sys.stdout.write(rendered + "\n")

    runtime = payload.get("runtime")
    if args.source == "runtime" and isinstance(runtime, dict) and not runtime.get("available", False):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
