## Context

See [proposal.md](proposal.md). MUX and DEMUX sketches already emit status over serial every 2 s. The Combination Devices page (`/combination`) implements MUX only. Valves dashboard patterns (serial parse → globals → WebSocket → truth-table highlight with X) are proven and reused here.

## Goals / Non-Goals

**Goals:**

- Rename Combination Devices → **Multiplexor** (`/multiplexor`, `static/multiplexor.html`)
- Add **Demultiplexor** page (`/demultiplexor`, `static/demultiplexor.html`) with DEMUX parser and 4-row truth table (X on inactive output)
- Update nav on all dashboards; remove `/combination`
- pytest coverage for DEMUX parser, both routes, and WebSocket cache

**Non-Goals:**

- Changing `mux.ino` or `demux.ino` serial format
- Browser control of input pins
- Combining MUX and DEMUX firmware in one upload

## Decisions

### Routes and file names

- **Decision:** `GET /multiplexor` → `static/multiplexor.html`; `GET /demultiplexor` → `static/demultiplexor.html`; remove `/combination` and `static/combination.html`
- **Rationale:** User-requested names; one page per device
- **Alternative:** Keep `/combination` as alias — rejected (breaking rename is explicit)

### DEMUX serial regex

- **Decision:** `^A=(\d)\s+DI=(\d)\s+->\s+Y0=(\d)\s+Y1=(\d)(?:\s+\(selected: Y[01]\))?$`
- **Rationale:** Matches `demux.ino` output; tolerant of optional suffix
- **Alternative:** Strict full-line match — rejected; fragile

### WebSocket event shapes

- **Decision:** Keep `{"type": "mux", ...}` unchanged; add `{"type": "demux", "a", "di", "y0", "y1", "cached"?}`
- **Rationale:** Separate event types per sketch; consistent with valves/mux pattern

### Truth tables with X

- **Decision:** Multiplexor — 4 rows, X on inactive DI column (existing `MUX_TRUTH_TABLE` pattern). Demultiplexor — 4 rows, X on inactive Y output (Y1 when A=0, Y0 when A=1)
- **Rationale:** Matches MUX teaching table; highlights only the row matching live (A, DI) or (A, active DI)
- **Highlight rule (MUX):** `a === currentA && (a === 0 ? di0 === currentDi0 : di1 === currentDi1)`
- **Highlight rule (DEMUX):** `a === currentA && di === currentDi`

### Nav accent colors

- **Decision:** Multiplexor keeps emerald `#34d399`; Demultiplexor uses rose `#fb7185` for active nav border
- **Rationale:** Visual distinction between sibling pages

### Parser placement in `read_serial`

- **Decision:** Check DEMUX pattern after MUX, before display/keypad parsers
- **Rationale:** MUX and DEMUX line formats are distinct; order avoids false matches

### Test file

- **Decision:** Rename `pytest/test_combination.py` → `pytest/test_mux_demux.py` (or extend in place if rename is heavy — prefer rename for clarity)
- **Rationale:** Covers both devices after split

## Risks / Trade-offs

- **[Risk] User uploads wrong sketch** → Widgets stay pending/error; mitigated by page subtitle ("requires mux.ino" / "requires demux.ino")
- **[Risk] COM8 shared** → One sketch per session; same as existing dashboards
- **[Trade-off] 2 s serial interval** → Slow widget updates; acceptable, matches firmware

## Migration Plan

1. Implement on `feature-mux-demux-pages` branch
2. Deploy backend + static files; `/combination` returns 404
3. Users reflash correct sketch per page and update bookmarks to `/multiplexor`

No database migration.

## Open Questions

None.
