## Why

The Combination Devices dashboard bundles MUX logic under a generic name, while DEMUX now has its own firmware (`arduino/demux/demux.ino`) with no matching web UI. Splitting into dedicated **Multiplexor** and **Demultiplexor** pages gives each combinational device a clear home, consistent with the one-sketch-per-page pattern used elsewhere in the project.

## What Changes

- Rename the existing Combination Devices page to **Multiplexor** (title, nav label, route `/multiplexor`); keep MUX widgets and 8-row truth table with **X** don't-care cells
- Add a new **Demultiplexor** page at `/demultiplexor` backed by `arduino/demux/demux.ino` serial output
- Add DEMUX serial parsing, WebSocket events, and status API fields (`last_demux_a`, `last_demux_di`, `last_demux_y0`, `last_demux_y1`)
- Demultiplexor page: four widgets (A, DI, Y0, Y1) and a 4-row truth table with **X** where outputs are don't-care for inactive paths
- Update sidebar nav on all dashboards: replace **Combination Devices** with **Multiplexor** and **Demultiplexor** links
- **BREAKING**: remove `/combination` route and `static/combination.html` (replaced by `/multiplexor`)

## Capabilities

### New Capabilities

- `demultiplexor-display`: DEMUX serial ingestion from `demux.ino`, Demultiplexor dashboard, live widgets, and truth-table row highlighting

### Modified Capabilities

- `combination-devices-display`: rename and narrow scope to Multiplexor only; route and nav label changes (archived spec path from prior change — delta updates requirements for MUX page naming and URL)

## Impact

- **Arduino**: `arduino/mux/mux.ino` for Multiplexor; `arduino/demux/demux.ino` for Demultiplexor (no firmware changes in this change)
- **Backend**: `main.py` — DEMUX parser, `notify_demux` / WebSocket `demux` events, `/multiplexor` and `/demultiplexor` routes; remove `/combination`
- **Frontend**: rename `static/combination.html` → `static/multiplexor.html`; new `static/demultiplexor.html`; nav updates in all `static/*.html`
- **Tests**: extend `pytest/test_combination.py` (or rename) for DEMUX parser, both page routes, and WebSocket cache

## Non-Goals

- Changing `mux.ino` or `demux.ino` serial format
- Browser control of Arduino input pins
- Combining MUX and DEMUX in a single firmware upload
- Server-side history or charts
