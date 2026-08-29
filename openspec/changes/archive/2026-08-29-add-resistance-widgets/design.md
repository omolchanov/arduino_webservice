## Context

See [proposal.md](proposal.md). The Digital Signal dashboard parses `Pot:` lines from `arduino/simple01.ino` for potentiometer voltage, detected logic state, and current. The sketch now appends `| LED Resistance: X.X Ohm` to each `Pot:` line, which breaks the existing `POT_PATTERN` regex and leaves resistance data unexposed in the UI.

## Goals / Non-Goals

**Goals:**

- Restore pot/detected/current parsing for the extended `Pot:` line format with LED resistance suffix
- Parse and broadcast LED resistance (Ω) as a first-class WebSocket/status channel
- Add live resistance widget and resistance history chart on `/digital` using existing card/chart/status-dot patterns
- Place resistance history immediately after the mA history widget; use **Ω** as the unit label in both widgets

**Non-Goals:**

- LED voltage display or WebSocket broadcast
- Shunt voltage display or WebSocket broadcast
- Arduino firmware changes
- Changes to Keypad or Sensors pages

## Decisions

### 1. Extend `parse_pot_line` return type

**Choice:** Return `tuple[float, float, float | None, float | None]` — `(pot_v, detected, current_ma, resistance_ohm)`.

- `resistance_ohm` is `None` when the line has no `LED Resistance:` field (backward-compatible)
- `read_serial` calls `notify_resistance(ohm)` only when `resistance_ohm is not None`
- Current field remains optional and independent of resistance

**Alternative:** Separate `parse_resistance_line` regex — rejected; resistance is always on the same `Pot:` line.

### 2. Extended regex with optional resistance suffix

**Choice:**

```python
POT_PATTERN = re.compile(
    r"^Pot:\s*([\d.]+)\s*V\s*\|\s*Logic:\s*(0|UNDEFINED|1)"
    r"(?:\s*\|\s*PWM:\s*\d+)?"
    r"(?:\s*\|\s*Shunt:\s*[\d.]+\s*V)?"
    r"(?:\s*\|\s*Current:\s*([\d.]+)\s*mA)?"
    r"(?:\s*\|\s*LED Resistance:\s*([\d.]+)\s*Ohm)?$"
)
```

**Rationale:** Matches `simple01.ino` output exactly; old lines without resistance still match.

### 3. Backend mirrors current channel pattern

**Choice:** Add `last_led_resistance_ohm`, `notify_resistance`, `broadcast_resistance`, status API field, and WebSocket cache-on-connect using the same structure as `current`.

- WebSocket payload: `{"type": "resistance", "ohm": <float>}`
- Status API field: `last_led_resistance_ohm`

**Rationale:** Consistent with existing digital-display channels; minimal new surface area.

### 4. UI: live card + history chart

**Choice:** Add two cards on `/digital`:

| Widget | Pattern source | Display |
|--------|----------------|---------|
| Resistance | Current card | Large value (1 decimal) + **Ω** unit, status dot |
| Resistance history | Current history card | Chart.js line chart, 120s window, localStorage |

- Live card placed in top row after the Current card
- History card placed immediately after "Shunt resistor history, mA"
- Accent color: `#f97316` (orange — distinct from blue/purple/emerald/amber widgets)
- Y-axis: 0–2000 Ω (step 500); covers typical LED dynamic resistance range
- Register `widgets.resistance` for status-dot lifecycle
- Include in Clear button and `beforeunload` save (`digital-resistance-history` key)

**Alternative:** Combine resistance into current card — rejected; user requested separate widgets matching existing UX.

## Risks / Trade-offs

- **[Risk] Parser mismatch if firmware format drifts** → Regex anchored to exact `simple01.ino` field order; unit tests cover full and legacy line formats.
- **[Risk] Pot/detected/current widgets silent on new firmware before deploy** → Deploy `main.py` and `digital.html` together; noted as BREAKING in proposal.
- **[Risk] Y-axis 2000 Ω may clip unusual circuits** → Acceptable for LED-on-D9 design; can widen later without API changes.
- **[Risk] Zero resistance when current is near zero** → Firmware sets `ledResistance = 0` when `current <= 0.0001`; UI displays `0.0` — matches firmware behavior.

## Migration Plan

1. Deploy updated `main.py` and `static/digital.html` together.
2. Ensure `arduino/simple01.ino` with LED resistance output is flashed; close Serial Monitor; restart uvicorn (release COM8 first).
3. Rollback: revert both files; re-flash prior firmware if rolling back sketch too.
