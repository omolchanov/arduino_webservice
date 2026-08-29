## Why

The Digital Signal dashboard shows live readings for potentiometer, detected logic LED, current, and resistance in a single value row, but the button-driven **Logic signal LED** (`Signal: 0|1` on D8) only appears as an inline value inside its history graph card. That inconsistency makes the primary signal harder to scan at a glance and leaves the value row at four columns while a fifth measurement already exists in the backend.

## What Changes

- Add a **Logic signal LED** live value widget in the top value row, displaying the current `0` or `1` state from `last_logic_value` / WebSocket `logic` events
- Update the value row layout so all **five** live widgets (potentiometer, detected logic LED, current, resistance, logic signal LED) appear in one row
- Move the logic status dot to the new value widget header (same online/offline pattern as the other four widgets)
- Simplify the **Logic signal LED history** graph card to chart-only, matching the other history graphs (no duplicate large inline value)
- **No backend changes** — `last_logic_value`, WebSocket `logic` events, and serial parsing already exist

## Capabilities

### New Capabilities

_None — all behavior extends the existing digital-display capability._

### Modified Capabilities

- `digital-display`: Add a logic signal LED live value widget; require all five live widgets in one row; update logic signal graph widget to be history-only (no inline current-value display).

## Impact

- **Arduino**: `arduino/simple01.ino` — no firmware changes
- **Backend**: `main.py` — no changes expected
- **Frontend**: `static/digital.html` — new value card, CSS grid column count, refactor logic dot handling into the shared widgets pattern, trim graph card markup
- **Tests**: none expected (frontend-only layout; existing parser/API tests unchanged)
- **Specs**: `openspec/specs/digital-display/spec.md` — new logic signal LED widget requirement and layout/graph updates
