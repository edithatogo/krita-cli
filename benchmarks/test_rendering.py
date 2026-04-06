"""Performance benchmarks for krita_client and plugin rendering."""

from __future__ import annotations

import importlib.util
import time
from pathlib import Path


def _get_plugin_class() -> type:
    """Import the plugin module via file path (not a pip-installable package)."""
    plugin_path = Path(__file__).parent.parent / "krita-plugin" / "kritamcp" / "__init__.py"
    spec = importlib.util.spec_from_file_location("kritamcp", plugin_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module.KritaMCPExtension  # type: ignore[no-any-return]


def benchmark_stroke_rendering_python() -> float:
    """Benchmark pure Python stroke rendering."""
    plugin_cls = _get_plugin_class()

    pixels = bytearray(255 * 255 * 4)
    w, h = 255, 255
    points = [[i * 10, i * 10] for i in range(25)]
    radius = 20
    hardness = 0.5
    opacity = 1.0
    r, g, b = 255, 0, 0

    start = time.perf_counter()
    plugin_cls._draw_stroke_python(pixels, w, h, points, radius, hardness, opacity, r, g, b)
    return time.perf_counter() - start


def benchmark_stroke_rendering_numpy() -> float:
    """Benchmark numpy-accelerated stroke rendering."""
    try:
        import numpy as np  # noqa: F401, PLC0415
    except ImportError:
        return 0.0

    plugin_cls = _get_plugin_class()

    pixels = bytearray(255 * 255 * 4)
    w, h = 255, 255
    points = [[i * 10, i * 10] for i in range(25)]
    radius = 20
    hardness = 0.5
    opacity = 1.0
    r, g, b = 255, 0, 0

    start = time.perf_counter()
    plugin_cls._draw_stroke_numpy(pixels, w, h, points, radius, hardness, opacity, r, g, b)
    return time.perf_counter() - start


if __name__ == "__main__":
    python_time = benchmark_stroke_rendering_python()
    numpy_time = benchmark_stroke_rendering_numpy()

    print(f"Python stroke rendering: {python_time:.4f}s")
    if numpy_time > 0:
        print(f"Numpy stroke rendering:  {numpy_time:.4f}s")
        print(f"Speedup: {python_time / numpy_time:.1f}x")
    else:
        print("Numpy not available — skipping numpy benchmark")
