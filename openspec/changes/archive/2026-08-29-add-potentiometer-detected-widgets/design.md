## Context

The Digital Signal dashboard at `/digital` already parses `Generated: 0|1` from `arduino/simple01.ino` and drives the **Logic signal LED** graph widget (D8). The sketch prints a single combined line every second:

```
Generated: 1 | Potentiometer: 2.50 V | Detected: 1
```

`Potentiometer` reflects ADC voltage on A0; `Detected` is the thresholded logic state that drives the **second LED** on D9 (`LED_LOGIC_PIN`). See proposal.md for motivation.

**Constraint:** the existing Logic signal LED card (graph, current value, status dot, localStorage history, Clear button) must remain unchanged.

## Goals / Non-Goals

**Goals:**

- Parse potentiometer voltage and detected logic from the same `simple01.ino` serial lines
- Broadcast `potentiometer` and `detected` WebSocket events; cache on connect
- Extend `GET /api/status` with last values for both readings
- Add two new cards on `/digital` using Sensors-style value display (large number + unit/label, status dot)

**Non-Goals:**

- Changes to `arduino/simple01.ino` or the Logic signal LED widget
- Graphs or history buffers for the new widgets (live value only, like Sensors distance/light)
- Combining with other sketches on COM8

## Decisions

### 1. Single-line parser for all three fields

Replace the narrow `LOGIC_PATTERN` match with one regex that captures all three fields from a complete `simple01.ino` line:

| Group | Example | Use |
|-------|---------|-----|
| `Generated` | `1` | Existing `logic` broadcast (unchanged) |
| `Potentiometer` | `2.50` | New `potentiometer` broadcast |
| `Detected` | `1` | New `detected` broadcast |

Regex (illustrative):

```
^Generated:\s*([01])\s*\|\s*Potentiometer:\s*([\d.]+)\s*V\s*\|\s*Detected:\s*([01])$
```

`parse_simple01_line(line) -> tuple[int, float, int] | None` returns all three values or `None` if the line does not match. `read_serial()` calls it once per line and invokes `notify_logic`, `notify_potentiometer`, and `notify_detected` in sequence.

**Alternative considered:** three separate regexes on the same line — rejected because one atomic parse avoids partial updates if the line format drifts.

### 2. WebSocket message types

```json
{"type": "potentiometer", "v": 2.5}
{"type": "detected", "value": 1}
```

On connect, send cached values with `"cached": true` when available (same pattern as `logic`, `distance`, `light`).

### 3. Status API

Extend `GET /api/status`:

```json
{
  "last_logic_value": 1,
  "last_potentiometer_v": 2.5,
  "last_detected_value": 1
}
```

Each field is a number or `null` when no reading has been received.

### 4. Digital page UI (`static/digital.html`)

Add two standard-width cards above the existing full-width Logic signal LED card:

| Card | Header | Body | Accent |
|------|--------|------|--------|
| Potentiometer | **Potentiometer** + status dot | Large voltage (2 decimals) + `V` unit | Reuse `.distance-value` / `.distance-unit` from Sensors |
| Detected logic LED | **Detected logic LED** + status dot | Large `0` or `1` + `detected` label | Same typography as logic current value but distinct card |

- Reuse Sensors status-dot lifecycle (initializing → ok on live reading → error on timeout/offline)
- Handle WebSocket `potentiometer` and `detected` events; seed from `/api/status` on load
- Do not modify Logic signal LED card markup, chart config, history, or Clear button behavior

**Layout:** `.dashboard` grid already supports `repeat(auto-fill, minmax(320px, 1fr))` — two new cards sit in the top row; Logic signal LED remains `card-wide` below.

### 5. Hardware mapping (documentation only)

| Sketch symbol | Pin | Widget |
|---------------|-----|--------|
| `SIGNAL_PIN` | D8 | Logic signal LED (existing, no change) |
| `LED_LOGIC_PIN` | D9 | Detected logic LED (new widget shows `Detected` value) |
| `POT_PIN` | A0 | Potentiometer (new widget shows voltage) |

## Risks / Trade-offs

- **[Partial line match]** → Require full-line regex; malformed lines are ignored entirely (no partial broadcasts)
- **[Voltage precision]** → Display two decimal places to match sketch `Serial.print(voltage, 2)`
- **[Widget naming]** → "Detected logic LED" distinguishes D9 state from D8 "Logic signal LED"

## Migration Plan

1. Deploy backend parser + API + WebSocket changes
2. Update `static/digital.html` with two new cards
3. User keeps `simple01.ino` uploaded (no sketch change)
4. Rollback: revert `main.py` and `digital.html`; existing logic widget continues to work
