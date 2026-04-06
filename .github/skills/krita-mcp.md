# Krita MCP — Skill Reference

## What is this?

A **SOTA CLI + MCP server** for programmatic painting in Krita. Two interfaces, one core:
- **CLI**: `krita stroke --points 100,100 200,200` — direct command-line control
- **MCP**: FastMCP server — for AI agents to paint programmatically

Both talk to a Krita plugin via HTTP on localhost:5678.

## Quick Start

### Prerequisites
- Python 3.12+
- Krita installed with MCP plugin enabled
- `uv` package manager

### Setup
```bash
uv sync
# Copy plugin to Krita's plugin directory
# Enable in Krita: Settings → Configure Krita → Python Plugin Manager
# Start Krita with plugin enabled
```

### CLI Usage
```bash
# Check Krita is running
krita health

# Create a canvas
krita canvas new-canvas --width 1920 --height 1080

# Set color and draw
krita color set-color --color "#ff0000"
krita stroke stroke "0,0" "100,100" "200,50"

# Select and draw within bounds
krita selection select-rect --x 10 --y 10 --width 100 --height 100
krita stroke stroke "0,0" "200,200"  # clipped to selection

# Export canvas
krita canvas get-canvas --filename output.png
```

### MCP Usage

Connect an MCP client (Claude, etc.) to `http://localhost:5678`. Available tools:

| Tool | Description |
|------|-------------|
| `krita_health` | Check Krita + plugin status |
| `krita_new_canvas` | Create canvas (width, height, bg color) |
| `krita_set_color` | Set foreground color (hex) |
| `krita_set_brush` | Set brush preset/size/opacity |
| `krita_stroke` | Paint stroke through [x, y] points |
| `krita_fill` | Fill circular area |
| `krita_draw_shape` | Draw rectangle/ellipse/line |
| `krita_get_canvas` | Export canvas to PNG |
| `krita_save` | Save canvas to file |
| `krita_undo` / `krita_redo` | Undo/redo |
| `krita_clear` | Clear canvas |
| `krita_get_color_at` | Eyedropper |
| `krita_list_brushes` | List brush presets |
| `krita_open_file` | Open existing file |
| `krita_batch` | Execute multiple commands sequentially |
| `krita_rollback` | Roll back a batch operation by batch ID |
| `krita_select_rect` | Select a rectangular area |
| `krita_select_ellipse` | Select an elliptical area |
| `krita_select_polygon` | Select a polygonal area |
| `krita_selection_info` | Get current selection bounds |
| `krita_invert_selection` | Invert the current selection |
| `krita_clear_selection` | Clear selection contents |
| `krita_fill_selection` | Fill selection with foreground color |
| `krita_deselect` | Remove current selection |
| `krita_transform_selection` | Move/rotate/scale selection |
| `krita_grow_selection` | Grow selection by N pixels |
| `krita_shrink_selection` | Shrink selection by N pixels |
| `krita_border_selection` | Create border around selection |
| `krita_get_capabilities` | Get detected API capabilities |
| `krita_security_status` | Get security limits and usage |
| `krita_list_tools` | List all available MCP tools |

## Agent Workflow

### Painting a simple shape
1. `krita_new_canvas(width=800, height=600)` — create canvas
2. `krita_set_color(color="#ff0000")` — set color
3. `krita_stroke(points=[[100,100],[200,100],[150,200]])` — draw triangle
4. `krita_get_canvas(filename="result.png")` — export result

### Painting within a selection
1. `krita_new_canvas(width=800, height=600)`
2. `krita_select_rect(x=50, y=50, width=200, height=200)` — create selection
3. `krita_set_color(color="#00ff00")`
4. `krita_stroke(points=[[0,0],[400,400]])` — clipped to selection
5. `krita_deselect()` — remove selection
6. `krita_get_canvas(filename="clipped.png")`

### Batch operations
1. `krita_batch(commands=[{"action":"set_color","params":{"color":"#ff0000"}},{"action":"stroke","params":{"points":[[0,0],[100,100]]}}])`
2. `krita_rollback(batch_id="...")` — if something went wrong

### Iterative painting
1. `krita_new_canvas()` → `krita_stroke()` → `krita_get_canvas()` — see result
2. Analyze result, adjust parameters
3. `krita_stroke()` with new points → `krita_get_canvas()` — iterate
4. `krita_save(path="final.png")` when satisfied

## Security Limits

| Limit | Default |
|-------|---------|
| Rate limit | 60 commands/minute |
| Max payload | 10 MB |
| Max batch size | 50 commands |
| Max canvas | 8192×8192 |
| Max layers | 100 |

Check current status: `krita selection security-status`

## Command Groups

| Group | Commands |
|-------|----------|
| `krita canvas` | new-canvas, get-canvas, save, clear |
| `krita color` | set-color, get-color-at |
| `krita brush` | set-brush, list-brushes |
| `krita stroke` | stroke, fill, draw-shape |
| `krita navigation` | undo, redo |
| `krita file` | open-file |
| `krita selection` | select-rect, select-ellipse, select-polygon, selection-info, transform-selection, grow-selection, shrink-selection, border-selection, select-clear, select-invert, select-fill, deselect, security-status |
| `krita history` | history |
| `krita introspect` | canvas-info, current-color, current-brush |
| `krita replay` | replay |

## Error Handling

All commands return structured errors:
```json
{"code": "NO_ACTIVE_DOCUMENT", "message": "...", "recoverable": true}
```

CLI shows: `[red]Error: ...[/red]` with hints for recovery.

## Protocol

- HTTP POST to `localhost:5678` with `{"action": "...", "params": {...}}`
- Health check: GET `localhost:5678/health`
- Default timeout: 30s (120s for export/save)
- Protocol version included in health response
