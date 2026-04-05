"""Performance benchmarks for krita_client and plugin rendering."""

from __future__ import annotations

import time


def benchmark_stroke_rendering_python() -> float:
    """Benchmark pure Python stroke rendering."""
    from krita_plugin.kritamcp import KritaMCPExtension

    pixels = bytearray(255 * 255 * 4)
    w, h = 255, 255
    points = [[i * 10, i * 10] for i in range(25)]
    radius = 20
    hardness = 0.5
    opacity = 1.0
    r, g, b = 255, 0, 0

    start = time.perf_counter()
    KritaMCPExtension._draw_stroke_python(pixels, w, h, points, radius, hardness, opacity, r, g, b)
    return time.perf_counter() - start


def benchmark_stroke_rendering_numpy() -> float:
    """Benchmark numpy-accelerated stroke rendering."""
    try:
        import numpy as np  # noqa: F401
    except ImportError:
        return 0.0

    from krita_plugin.kritamcp import KritaMCPExtension

    pixels = bytearray(255 * 255 * 4)
    w, h = 255, 255
    points = [[i * 10, i * 10] for i in range(25)]
    radius = 20
    hardness = 0.5
    opacity = 1.0
    r, g, b = 255, 0, 0

    start = time.perf_counter()
    KritaMCPExtension._draw_stroke_numpy(pixels, w, h, points, radius, hardness, opacity, r, g, b)
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
