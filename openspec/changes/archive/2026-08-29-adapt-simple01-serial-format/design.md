## Context

See [proposal.md](proposal.md). The Digital Signal dashboard and `main.py` parsers were built for a single combined serial line from `simple01.ino`. The sketch now emits separate `SIGNAL_PIN:` phase lines and `Pot:` reading lines, including a three-zone pot logic model (`0`, `UNDEFINED`, `1`).

## Goals / Non-Goals

**Goals:**

- Parse the new two-line-type serial protocol and restore live updates on `/digital`
- Represent pot-derived logic as numeric `0`, `0.5` (undefined), `1` end-to-end
- Show grey markers on the potentiometer graph when detected state enters the undefined zone (`0.5`)

**Non-Goals:**

- PWM value display or WebSocket broadcast
- Arduino firmware changes
- Changes to Keypad or Sensors pages

## Decisions

### 1. Two parsers instead of one combined regex

**Choice:** `parse_signal_pin_line()` for `SIGNAL_PIN: Logic 0|1 (…)` and `parse_pot_line()` for `Pot: X.XX V | Logic: …`.

**Rationale:** Matches the sketch's output structure; each line type maps to distinct widget updates. `read_serial` tries signal-pin before pot, then keypad.

**Alternative:** Single mega-regex — rejected; fragile and hard to test.

### 2. Encode UNDEFINED as `0.5`

**Choice:** Serial `Logic: UNDEFINED` → WebSocket/status `value: 0.5`.

**Rationale:** Keeps one numeric `detected` channel; UI can plot `0.5` on a stepped chart without a new event type.

**Alternative:** String `"undefined"` — rejected; breaks existing numeric handlers and chart math.

### 3. Pot graph markers: red / green / grey by target state

**Choice:** On any detected-state transition, place a marker on the pot history chart at the current pot voltage:

| Transition to | Marker color |
|---------------|--------------|
| `1` | Red (existing) |
| `0` | Green (existing) |
| `0.5` | Grey (new dataset) |

**Rationale:** Reuses `recordDetectedSwitch` / `potSwitchMarkers` pattern; grey visually distinct from HIGH/LOW.

### 4. PWM suffix accepted but ignored

**Choice:** `parse_pot_line` optional-regex tail `| PWM: N`; no broadcast.

**Rationale:** Matches sketch output without scope creep.

## Risks / Trade-offs

- **[Risk] Slower logic graph updates** — logic now updates on `SIGNAL_PIN` lines (~every 2s) not every pot line → acceptable; matches hardware phase timing.
- **[Risk] `0.5` float in JSON** — JavaScript `Number()` preserves `0.5`; status API returns float for `last_detected_value` when undefined → document in spec.
- **[Risk] Old `Generated:` lines ignored** — users must upload new `simple01.ino` → noted as BREAKING in proposal.

## Migration Plan

1. Deploy updated `main.py` and `static/digital.html` together.
2. User uploads current `arduino/simple01.ino` and restarts uvicorn (release COM8 first).
3. Rollback: revert both files; old sketch format would need to be re-flashed if rolling back firmware too.
