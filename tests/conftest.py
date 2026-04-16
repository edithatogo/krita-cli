"""Root conftest for adding krita-plugin to the Python path."""
import sys
from pathlib import Path

# Add krita-plugin directory to Python path for importing kritamcp module
plugin_dir = Path(__file__).parent.parent / "krita-plugin"
if str(plugin_dir) not in sys.path:
    sys.path.insert(0, str(plugin_dir))
