## Context

See [proposal.md](proposal.md). The MUX sketch (`arduino/mux/mux.ino`) already prints status every 2 s; Valves dashboard patterns (serial parse → globals → WebSocket → truth-table highlight) are proven in `main.py` and `static/valves.html`. MUX is read-only from the web — no serial write API.

## Goals / Non-Goals

**Goals:**

- Parse MUX serial lines and expose state via WebSocket and `GET /api/status`
- New `/combination` page with four widgets (A, DI0/DI1, DO/D13) and 8-row truth table with active-row highlight
- Nav link on all dashboards; pytest coverage for parser and API

**Non-Goals:**

- Browser control of D2/D3/D4 pins
- Changing MUX firmware or serial format
- EpoxyDuino/Wokwi changes in this change

## Decisions

### Route and page name

- **Decision:** `GET /combination` → `static/combination.html`, nav label **Combination Devices**
- **Rationale:** User-facing name from the request; URL is short and distinct from `/valves`
- **Alternative:** `/mux` — rejected as less descriptive for future combinational devices

### Serial regex

- **Decision:** Match `A=(\d)\s+DI0=(\d)\s+DI1=(\d)\s+->\s+DO=(\d)` with optional trailing `(selected: DI0|DI1)`
- **Rationale:** Matches current `mux.ino` output; tolerant of suffix text
- **Alternative:** Strict full-line match — rejected; fragile if banner text changes slightly

### WebSocket event shape

- **Decision:** `{"type": "mux", "a", "di0", "di1", "do", "cached"?}`
- **Rationale:** Mirrors `valve` events; lowercase field names consistent with JSON style in project
- **Alternative:** Reuse `valve` type — rejected; different semantics and truth table

### Page layout

- **Decision:** Copy Valves structure — sidebar, topbar, widget row (4 cards), truth table card below
- **Widgets:** Address (A), Data inputs (DI0, DI1), Output (DO / D13)
- **Truth table:** Static 8-row `MUX_TRUTH_TABLE` in JS; highlight when `a === currentA && di0 === currentDi0 && di1 === currentDi1`
- **Styling:** Reuse `.truth-table tr.active td` from Valves; accent color `#34d399` (emerald) for Combination Devices nav active state
- **Rationale:** User asked for Valves-style highlight; minimal new CSS

### Status API fields

- **Decision:** `last_mux_a`, `last_mux_di0`, `last_mux_di1`, `last_mux_do` on `GET /api/status`
- **Rationale:** Consistent with `last_valve_*` naming

### Parser placement in `read_serial`

- **Decision:** Check MUX pattern after valve/distance/light/pot parsers, before keypad
- **Rationale:** Same priority pattern as valves; MUX lines are distinct enough not to collide

## Risks / Trade-offs

- **[Risk] User uploads wrong sketch** → Page shows offline/pending widgets; mitigated by spec note and dashboard subtitle ("requires mux.ino")
- **[Risk] COM8 shared with other dashboards** → Same as existing pages; one sketch per session is documented
- **[Trade-off] 2 s serial interval** → Widgets update slowly; acceptable, matches firmware `printInterval`

## Migration Plan

1. Implement backend parser and route on `feature-combination-devices` branch
2. Add `static/combination.html` and nav links
3. Add pytest tests
4. User uploads `mux.ino` and opens `/combination` while uvicorn runs

No rollback complexity — additive change only.

## Open Questions

None — scope is fully defined by the MUX sketch and Valves UI pattern.
