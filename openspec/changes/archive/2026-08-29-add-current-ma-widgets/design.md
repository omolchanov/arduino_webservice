## Context

See [proposal.md](proposal.md). The Digital Signal dashboard parses `Pot:` lines from `arduino/simple01.ino` for potentiometer voltage and detected logic state. The sketch now appends `| Shunt: X.XXX V | Current: X.X mA` to each `Pot:` line, which breaks the existing `POT_PATTERN` regex and leaves current data unexposed in the UI.

## Goals / Non-Goals

**Goals:**

- Restore pot/detected parsing for the extended `Pot:` line format
- Parse and broadcast current (mA) as a first-class WebSocket/status channel
- Add live current widget and current history chart on `/digital` using existing card/chart/status-dot patterns

**Non-Goals:**

- Shunt voltage display or WebSocket broadcast
- PWM value display or WebSocket broadcast
- Arduino firmware changes
- Changes to Keypad or Sensors pages

## Decisions

### 1. Extend `parse_pot_line` return type

**Choice:** Return `tuple[float, float, float | None]` — `(pot_v, detected, current_ma)`.

- `current_ma` is `None` when the line has no `Current:` field (backward-compatible)
- `read_serial` calls `notify_current(ma)` only when `current_ma is not None`
- Shunt voltage is accepted in the regex but not broadcast (same as PWM)

**Alternative:** Separate `parse_current_line` regex — rejected; current is always on the same `Pot:` line.

### 2. Extended regex with optional suffix

**Choice:**

```python
POT_PATTERN = re.compile(
    r"^Pot:\s*([\d.]+)\s*V\s*\|\s*Logic:\s*(0|UNDEFINED|1)"
    r"(?:\s*\|\s*PWM:\s*\d+)?"
    r"(?:\s*\|\s*Shunt:\s*[\d.]+\s*V)?"
    r"(?:\s*\|\s*Current:\s*([\d.]+)\s*mA)?$"
)
```

**Rationale:** Matches `simple01.ino` output exactly; old lines without shunt/current still match.

### 3. Backend mirrors potentiometer pattern

**Choice:** Add `last_current_ma`, `notify_current`, `broadcast_current`, status API field, and WebSocket cache-on-connect using the same structure as `potentiometer`.

**Rationale:** Consistent with existing digital-display channels; minimal new surface area.

### 4. UI: live card + history chart

**Choice:** Add two cards on `/digital`:

| Widget | Pattern source | Display |
|--------|----------------|---------|
| Current | Potentiometer card | Large value (1 decimal) + `mA` unit, status dot |
| Current history | Potentiometer history card | Chart.js line chart, 120s window, localStorage |

- Accent color: `#34d399` (emerald — distinct from blue/purple/yellow widgets)
- Y-axis: 0–500 mA (10 Ω shunt + 5 V ADC ceiling = 500 mA max)
- Register `widgets.current` for status-dot lifecycle
- Include in Clear button and `beforeunload` save (`digital-current-history` key)

**Alternative:** Combine current into potentiometer card — rejected; user requested separate widgets matching existing UX.

## Risks / Trade-offs

- **[Risk] Parser mismatch if firmware format drifts** → Regex anchored to exact `simple01.ino` field order; unit tests cover full and legacy line formats.
- **[Risk] Pot/detected widgets silent on new firmware before deploy** → Deploy `main.py` and `digital.html` together; noted as BREAKING in proposal.
- **[Risk] Y-axis 500 mA may clip unusual circuits** → Acceptable for 10 Ω shunt design; can widen later without API changes.

## Migration Plan

1. Deploy updated `main.py` and `static/digital.html` together.
2. Ensure `arduino/simple01.ino` with current measurement is flashed; close Serial Monitor; restart uvicorn (release COM8 first).
3. Rollback: revert both files; re-flash prior firmware if rolling back sketch too.
