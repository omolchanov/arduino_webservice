## Context

The project has Keypad (`/`), Sensors (`/sensors`), and Digital Signal (`/digital`) dashboards sharing one serial connection on COM8 at 9600 baud. `arduino/valves.ino` reads two button inputs (A on D2, B on D3), computes AND/OR logic, drives an LED on D9, and prints status every 1 second — but `main.py` does not parse valve lines or send gate commands. See proposal.md for motivation.

**Architecture rule:** one Arduino sketch per dashboard page. The Valves dashboard is backed exclusively by `arduino/valves.ino`.

```
/valves dashboard
  └── Gate / Inputs / Output widgets + truth table  →  arduino/valves.ino
```

## Goals / Non-Goals

**Goals:**

- Parse valve status serial lines and broadcast live A/B/Y/gate values over WebSocket
- Send gate selection commands (`A`/`O`) to Arduino when user changes dropdown
- New `/valves` page with gate dropdown, three live widgets, and truth table
- Reuse Digital Signal / Sensors page styling (sidebar, dark cards, status badge, custom notifications)
- Add Valves nav link across all pages

**Non-Goals:**

- Changing `arduino/valves.ino` serial format
- Additional gate types beyond AND/OR
- Server-side history storage or charts
- Combining valves firmware with other sketches

## Decisions

### 1. Dedicated sketch for the Valves dashboard

| Dashboard | Sketch |
|-----------|--------|
| Valves | `arduino/valves.ino` |

User uploads `valves.ino` when using `/valves`. Only one sketch runs on COM8 at a time (same constraint as other pages).

### 2. Serial parser

Add `parse_valve_line(line) -> tuple[int, int, int, str] | None`:

| Input | Result |
|-------|--------|
| `A = 0 \| B = 1 \| Y = 0 \| Gate = AND` | `(0, 1, 0, "AND")` |
| `A = 1 \| B = 1 \| Y = 1 \| Gate = OR` | `(1, 1, 1, "OR")` |
| Other lines | delegate to existing parsers |

Regex: `^A\s*=\s*(\d)\s*\|\s*B\s*=\s*(\d)\s*\|\s*Y\s*=\s*(\d)\s*\|\s*Gate\s*=\s*(AND|OR)$`

Russian boot/confirmation lines (`Выбран AND`, menu text) are ignored.

In `read_serial()`, check valve lines after pot/signal parsers, before keypad.

### 3. WebSocket messages

Single atomic message per reading:

```json
{"type": "valve", "a": 0, "b": 1, "y": 0, "gate": "AND"}
```

On connect, send last known valve state if available with `"cached": true`.

**Alternative considered:** separate `valve_input` and `valve_output` messages — rejected because the sketch reports all fields in one line; a single message keeps UI state consistent.

### 4. Gate selection API (serial write)

```
POST /api/valve/gate
Body: {"gate": "AND" | "OR"}
```

- Validate gate value; return 400 for invalid gate
- Return 503 if serial disconnected
- Thread-safe write on `serial_port`: send `b"A"` for AND, `b"O"` for OR
- Return `{"ok": true, "gate": "AND"}` on success

This is the first serial write in the project. Use the existing `serial_port` global with a lock to avoid concurrent read/write issues.

### 5. Status API

Extend `GET /api/status`:

```json
{
  "last_valve_a": 0,
  "last_valve_b": 1,
  "last_valve_y": 0,
  "last_valve_gate": "AND"
}
```

All fields are `null` when no reading has been received.

### 6. Valves page UI (`static/valves.html`)

- Copy layout/CSS from `static/digital.html`: `.layout`, `.sidebar`, `.topbar`, `.card`, `.app-status`, `.notification`
- Page title: **Valves**; nav accent: `#a78bfa` (violet)
- **Top bar (top-right):** gate dropdown (`<select>` AND/OR) placed left of the Online/Offline badge; on change calls `POST /api/valve/gate` with custom toast on success/error
- **Widget row (3 cards):**
  - **Selected gate** — large `AND` or `OR` from live serial + status dot
  - **Inputs** — `A: 0` and `B: 1` in one card + status dot
  - **Output** — large `Y: 0` or `1` + status dot
- **Truth table** — wide card below widgets with columns A, B, Y; 4 rows; Y values depend on selected gate (AND vs OR); highlight row matching current live A and B
- WebSocket `valve` events update widgets and truth-table highlight
- `/api/status` poll every 3s for connection badge and initial value seed
- Widget status-dot lifecycle: `initializing` → `ok` on first reading, `error` on offline (same pattern as Digital page)

### 7. Navigation

Add `<a href="/valves">Valves</a>` to `static/index.html`, `static/sensors.html`, `static/digital.html`, and `static/valves.html` (active on Valves page).

## Architecture

```
arduino/valves.ino → Serial "A = 0 | B = 1 | Y = 0 | Gate = AND"
                              ↓
                     parse_valve_line()
                              ↓
                     WebSocket broadcast
                              ↓
                     static/valves.html (widgets + truth table)

User dropdown → POST /api/valve/gate → serial write "A"/"O" → valves.ino
```

## Risks / Trade-offs

- **[One sketch on COM8]** → Document that user must upload `valves.ino` for the Valves dashboard
- **[First serial write]** → Use thread-safe write with lock; gate command may race with status reads — acceptable for this use case
- **[Dropdown vs live gate]** → Dropdown sends command; gate widget reflects Arduino-reported gate from serial (may lag briefly until next status line)
