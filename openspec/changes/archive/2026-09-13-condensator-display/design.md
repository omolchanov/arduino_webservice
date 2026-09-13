## Context

The project serves multiple Arduino dashboards over one COM8 serial connection at 9600 baud. `arduino/condensator/condensator.ino` alternates charge and discharge phases, printing phase markers and `V = <v> V   Q = <q> uC` lines once per second (10 samples per phase). See proposal.md for motivation.

**Architecture rule:** one Arduino sketch per dashboard. The Condensator page is backed exclusively by `arduino/condensator/condensator.ino`.

```
/condensator dashboard
  ├── Voltage widget (V + graph)   →  condensator.ino serial
  └── Charge Q widget (µC + graph) →  condensator.ino serial
```

Existing patterns to reuse: `static/digital.html` (Chart.js rolling graphs, dashed asymptote lines on potChart), `static/sensors.html` (layout, sidebar, status badge, custom notifications).

## Goals / Non-Goals

**Goals:**

- Parse condensator phase and measurement serial lines; broadcast via WebSocket
- New `/condensator` page with Voltage and Charge Q widgets (live value + Chart.js history)
- Dashed asymptote reference lines: 0 V / 5 V on voltage chart; 0 µC / 1100 µC on Q chart
- Phase indicator (Charging / Discharging) driven by serial phase markers
- Nav link on all dashboard pages; pytest for parser and route

**Non-Goals:**

- Firmware changes (use existing serial format from `condensator.ino`)
- Theoretical RC curve overlay (only horizontal asymptote lines, not exponential fit)
- Server-side persistence or multi-sketch multiplexing on COM8

## Decisions

### 1. Serial parser

Add `parse_condensator_line(line) -> tuple[float, float] | None`:

| Input | Result |
|-------|--------|
| `V = 2.45 V   Q = 539.0 uC` | `(2.45, 539.0)` |
| Other lines | `None` |

Regex: `^V\s*=\s*([\d.]+)\s+V\s+Q\s*=\s*([\d.]+)\s+uC$`

Phase lines handled separately (no regex on measurement parser):

| Input | WebSocket |
|-------|-----------|
| `Charging...` | `{"type": "condensator_phase", "phase": "charging"}` |
| `Discharging...` | `{"type": "condensator_phase", "phase": "discharging"}` |

In `read_serial()`, check condensator lines after existing parsers, before keypad.

### 2. WebSocket messages

Measurement:

```json
{"type": "condensator", "v": 2.45, "q_uc": 539.0}
```

Phase:

```json
{"type": "condensator_phase", "phase": "charging"}
```

On WebSocket connect, send last known `v`, `q_uc`, and `phase` with `"cached": true` when available (same pattern as distance/light).

### 3. Status API

Extend `GET /api/status` with optional fields:

```json
{
  "last_condensator_v": 2.45,
  "last_condensator_q_uc": 539.0,
  "last_condensator_phase": "charging"
}
```

### 4. Condensator page UI (`static/condensator.html`)

- Copy layout/CSS from `static/sensors.html` / `static/digital.html`
- Page title: **Condensator**; nav accent: `#38bdf8` (sky blue)
- Phase badge below title: **Charging** (green tint) / **Discharging** (amber tint) / **—** before first marker
- Two wide cards in a dashboard grid:
  1. **Voltage** — large value with **V** unit; Chart.js line chart (y: 0–5 V)
  2. **Charge Q** — large value with **µC** unit; Chart.js line chart (y: 0–1200 µC headroom)
- Asymptote lines (reuse digital.html potChart pattern): extra datasets with `borderDash: [6, 4]`, horizontal at 0 and max (5 V / 1100 µC)
- Chart.js v4 from CDN; rolling buffer ~120 points (~2 min at 1 s cadence)
- `localStorage` keys for history restore on reload (same pattern as digital page)
- Clear history button in page title row
- Custom toast notifications only

### 5. Navigation

Add `<a href="/condensator">Condensator</a>` to all pages with sidebar nav (`index.html`, `sensors.html`, `digital.html`, `valves.html`, `display.html`, `multiplexor.html`, `demultiplexor.html`, and any other nav-bearing static pages).

### 6. Tests

`pytest/test_condensator.py`:

- `parse_condensator_line` valid/invalid lines
- `GET /condensator` returns 200 and HTML containing Condensator title

## Risks / Trade-offs

- **[One sketch on COM8]** → User must upload `condensator.ino` when using this dashboard; document in AGENTS.md sketch table on apply
- **[Asymptotes are reference lines only]** → Dashed lines show 0/5 V and 0/1100 µC targets, not diode forward voltage; actual RC curve shape comes from live data
- **[Chart.js CDN]** → Consistent with digital page; no build step

## Migration Plan

1. Deploy backend parser + route
2. Add `static/condensator.html` and nav links
3. Upload `arduino/condensator/condensator.ino` to Arduino when testing
4. Rollback: remove route and nav links; parser ignores unknown lines harmlessly
