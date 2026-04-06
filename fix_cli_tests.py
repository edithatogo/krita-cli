import os
import glob

files = glob.glob("tests/integration/test_cli_*.py")

replacements = [
    ('["new-canvas"', '["canvas", "new-canvas"'),
    ('["set-color"', '["color", "set-color"'),
    ('["set-brush"', '["brush", "set-brush"'),
    ('["fill"', '["stroke", "fill"'),
    ('["draw-shape"', '["stroke", "draw-shape"'),
    ('["get-canvas"', '["canvas", "get-canvas"'),
    ('["clear"', '["canvas", "clear"'),
    ('["save"', '["canvas", "save"'),
    ('["list-brushes"', '["brush", "list-brushes"'),
    ('["get-color-at"', '["color", "get-color-at"'),
    ('["open-file"', '["file", "open-file"'),
    ('["undo"', '["navigation", "undo"'),
    ('["redo"', '["navigation", "redo"'),
]

for f in files:
    with open(f, 'r') as fh:
        content = fh.read()
    for old, new in replacements:
        content = content.replace(old, new)
    with open(f, 'w') as fh:
        fh.write(content)
    print(f"Fixed {f}")
