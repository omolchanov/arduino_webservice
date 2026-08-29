## Context

The project has Keypad (`/`) and Sensors (`/sensors`) dashboards sharing one serial connection on COM8 at 9600 baud. `arduino/simple01.ino` drives an LED on D8 (HIGH = ON, LOW = OFF), toggling every 1 second and sending `Logic 1 (HIGH) - LED ON` / `Logic 0 (LOW) - LED OFF` lines, but `main.py` does not parse them yet. See proposal.md for motivation.

**Architecture rule:** one Arduino sketch per widget. The logic graph widget is backed exclusively by `arduino/simple01.ino`.

```
/digital dashboard
  └── Logic signal graph widget  →  arduino/simple01.ino
```

## Goals / Non-Goals

**Goals:**

- Parse logic serial lines and broadcast live 0/1 values over WebSocket
- New `/digital` page with a Chart.js stepped line graph widget
- Reuse Sensors page styling (sidebar, dark cards, status badge, custom notifications)
- Add Digital Signal nav link across all pages

**Non-Goals:**

- Combining widgets into one sketch
- Server-side time-series storage
- Further changes to `simple01.ino` (sketch already updated with LED on D8)
- Multiple digital pins in phase 1

## Decisions

### 1. Dedicated sketch for the logic widget

| Widget | Sketch |
|--------|--------|
| Logic signal graph | `arduino/simple01.ino` |

User uploads `simple01.ino` when using `/digital`. Only one sketch runs on COM8 at a time (same constraint as Sensors vs Keypad).

### 2. Serial parser

Add `parse_logic_line(line) -> int | None`:

| Input | Result |
|-------|--------|
| `Logic 1 (HIGH) - LED ON` | `1` |
| `Logic 0 (LOW) - LED OFF` | `0` |
| Other lines | delegate to existing distance/light/key parsers |

Regex: `^Logic\s+([01])\s+\((HIGH|LOW)\)\s+-\s+LED\s+(ON|OFF)$`

D8 (`SIGNAL_PIN`) drives the LED: logic 1 → HIGH → LED ON; logic 0 → LOW → LED OFF.

In `read_serial()`, check logic lines after light, before keypad.

### 3. WebSocket messages

```json
{"type": "logic", "value": 1}
```

On connect, send last known logic value if available with `"cached": true` (same pattern as distance/light).

### 4. Status API

Extend `GET /api/status`:

```json
{
  "serial_connected": true,
  "com_port": "COM8",
  "ws_clients": 1,
  "last_distance_cm": null,
  "last_light_level": null,
  "last_logic_value": 1
}
```

### 5. Digital page UI (`static/digital.html`)

- Copy layout/CSS from `static/sensors.html`: `.layout`, `.sidebar`, `.topbar`, `.card`, `.app-status`, `.notification`
- Page title: **Digital Signal**; nav accent: `#fbbf24` (amber)
- Single card widget:
  - Header: **Logic signal** + status dot (reuse `.sensor-status-dot`)
  - Body: Chart.js stepped line chart (y-axis 0–1, stepSize 1)
  - Current value: large `0` or `1` with **LED OFF** / **LED ON** label (reuse `.distance-value` styling)
- Chart.js v4 from CDN
- Client rolling buffer: ~120 points (~2 min at 1s cadence from `simple01.ino`)
- WebSocket `logic` events append `{t, v}` and update chart
- `/api/status` poll every 3s for connection badge and initial value seed
- Custom toast notifications only (no `alert()`)

**Alternative considered:** native canvas drawing — rejected in favor of Chart.js for simpler stepped-line configuration and axis control.

### 6. Navigation

Add `<a href="/digital">Digital Signal</a>` to `static/index.html`, `static/sensors.html`, and `static/digital.html` (active on Digital page).

## Architecture

```
arduino/simple01.ino → Serial "Logic 1 (HIGH) - LED ON" / "Logic 0 (LOW) - LED OFF"
                              ↓
                     parse_logic_line()
                              ↓
                     WebSocket broadcast
                              ↓
                     static/digital.html (Chart.js graph)
```

## Risks / Trade-offs

- **[One sketch on COM8]** → Document that user must upload `simple01.ino` for the Digital dashboard
- **[Chart.js CDN]** → Acceptable for local dev; no build step required
- **[Y-axis clarity]** → Force min 0, max 1, stepSize 1 on chart config
