## Why

The Digital Signal dashboard currently shows only the generated logic signal (D8) from `arduino/simple01.ino`. The same sketch already prints potentiometer voltage and the detected logic state that drives the second LED (D9), but the web UI ignores that data. Exposing both readings on `/digital` gives a complete view of the experiment without changing the existing logic-signal graph widget.

## What Changes

- Parse `Potentiometer: <voltage> V` and `Detected: <0|1>` from existing `simple01.ino` serial lines (same line format as today)
- Broadcast new WebSocket events for potentiometer voltage and detected logic state
- Extend `GET /api/status` with `last_potentiometer_v` and `last_detected_value`
- Add two new dashboard cards on `/digital`:
  - **Potentiometer** — live voltage in volts (e.g. `2.50 V`)
  - **Detected logic LED** — live 0/1 state matching the second LED on D9
- **No changes** to the existing **Logic signal LED** graph widget (still driven by `Generated: 0|1` only)

## Capabilities

### New Capabilities

_None — all behavior extends the existing digital-display capability._

### Modified Capabilities

- `digital-display`: Extend serial ingestion, status API, WebSocket cache-on-connect, and dashboard UI with potentiometer voltage and detected-logic widgets; logic signal LED widget requirements remain unchanged.

## Impact

- **Arduino**: `arduino/simple01.ino` — no firmware changes (serial format already includes all fields)
- **Backend**: `main.py` — extend parser, state, broadcasts, status API, WebSocket connect cache
- **Frontend**: `static/digital.html` — two new cards reusing Sensors-style value display patterns
- **Specs**: `openspec/specs/digital-display/spec.md` — new requirements for potentiometer and detected widgets
