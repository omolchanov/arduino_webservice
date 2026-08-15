## Context

The updated Arduino sketch adds a status LED on D12 that blinks for 100ms on each valid key press. Serial output changed from a single character per line to a labeled line: `Pressed: 5`. A startup line `Keypad ready` is sent once after boot.

The Python server currently only accepts single-character lines (`len(line) == 1`). Without parser changes, all key presses would be ignored.

## Goals / Non-Goals

**Goals:**

- Replace `arduino/keypad.ino` with the LED-enabled sketch
- Parse `Pressed: <key>` lines in `main.py`
- Ignore `Keypad ready` and other non-key lines
- Preserve backward compatibility with legacy single-char serial format

**Non-Goals:**

- Remote LED control from the web UI
- Visual LED indicator in the browser
- Changing WebSocket message format

## Decisions

### 1. Serial line parser

Add `parse_key_line(line: str) -> str | None`:

| Input | Result |
|-------|--------|
| `Pressed: 5` | `5` |
| `5` (legacy) | `5` |
| `Keypad ready` | `None` (ignored) |
| `Pressed: Z` | `None` (invalid key) |

Use prefix `Pressed: ` (case-sensitive, matches Arduino `Serial.print`).

### 2. Arduino sketch

Adopt user-provided sketch as-is:

- `ledPin = 12`
- Blink HIGH 100ms on each debounced key press
- `Serial.print("Pressed: ")` + `Serial.println(key)`
- `Serial.println("Keypad ready")` in `setup()`

### 3. Boot banner handling

After serial connect and `reset_input_buffer()`, the first `Keypad ready` line may still arrive. Parser returns `None` — no broadcast, no error.

## Risks / Trade-offs

- **[Risk] Slower serial format** → negligible; one short line per key press
- **[Risk] LED pin conflicts** → D12 is standard; document in sketch comment
- **[Trade-off] No web LED mirror** → physical LED only; keeps scope minimal
