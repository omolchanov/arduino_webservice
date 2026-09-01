## Context

The `arduino/mulie_function/` folder contains a `MultiFunctionDisplay` class driving a 4-digit common-anode 7-segment display via two 74HC595 shift registers (pins 4/7/8). The demo sketch hardcodes `1234` with no buttons or serial. See proposal.md for motivation.

**Target behavior:** 3-button counter starting at **000** — each button increments one digit (0–9, wrap).

```
Button layout (left → right):
  D2 (left)    → hundreds digit
  D3 (middle)  → tens digit
  D5 (right)   → ones digit
```

Display pins unchanged: latch=4, clock=7, data=8.

## Goals / Non-Goals

**Goals:**

- 3-button counter firmware: boot at 000, debounced increment per digit
- Extract `display_math.h` with `increment_digit()` and value/digit conversion (testable)
- Serial protocol: `Display: <n>` on change (0–999), `S<n>` to set remotely
- Backend parser, WebSocket, status API, set-value API, `/display` page
- EpoxyDuino + pytest tests

**Non-Goals:**

- Fourth-digit input (hardware digit 0 stays 0; value range 0–999)
- Changing shift-register wiring or segment maps
- Combining with other sketches

## Decisions

### 1. Button wiring and debounce

| Pin | Role |
|-----|------|
| D2 | Left button → hundreds |
| D3 | Middle button → tens |
| D5 | Right button → ones |

All `INPUT_PULLUP`, active LOW. Reuse debounce pattern from `simple01.ino` (50 ms, per-button state). Pins chosen to avoid conflict with display (4, 7, 8).

**Alternative considered:** single shared button with mode switch — rejected; user specified 3 dedicated buttons.

### 2. Counter state model

Store value as `int counter` (0–999). On button press:

```cpp
byte hundreds = counter / 100;
byte tens     = (counter / 10) % 10;
byte ones     = counter % 10;
// increment the pressed digit with wrap 0-9
counter = hundreds * 100 + tens * 10 + ones;
display.show(counter);  // shows 0000-0999; digits[0] is thousands (always 0)
```

`MultiFunctionDisplay::show()` already splits into 4 digits; value 42 → `0042` on hardware, visually `042` if leading zero suppressed or `0042` zero-padded.

Add `increment_digit(byte &d)` in `display_math.h`: `d = (d + 1) % 10`.

### 3. Sketch structure (`mulie_function.ino`)

Rename `sketch_sep1a.ino` → `mulie_function.ino`:

```
setup():
  display.begin()
  setup buttons (INPUT_PULLUP)
  counter = 0; display.show(0)
  Serial.begin(9600)

loop():
  display.update()          // keep multiplexing alive
  handleButton(left)  → inc hundreds
  handleButton(middle)→ inc tens
  handleButton(right) → inc ones
  handleSerial()            // S<n> set command
  if value changed → Serial.println("Display: " + counter)
```

Call `display.update()` every loop iteration (before button reads) to prevent flicker.

### 4. Serial protocol

**Output** (on value change from button or serial command):

```
Display: 42
```

**Input** (remote set from dashboard):

```
S567
```

Clamp to 0–999. Update `counter` and `display.show(counter)`.

### 5. Backend (`main.py`)

`parse_display_line(line) -> int | None` — regex `^Display:\s*(\d{1,3})$`, clamp 0–999.

WebSocket: `{"type": "display", "value": n}`.

`POST /api/display/value` — body `{"value": 0-999}`, writes `S{n}\n`.

### 6. Frontend (`static/display.html`)

- Large 3-digit readout (zero-padded `000`–`999`)
- Number input + Set button
- Reuse sidebar/card/toast patterns from Valves page

### 7. Tests

| Layer | Coverage |
|-------|----------|
| `display_math.h` | `increment_digit` wrap 9→0; value rebuild after digit increment |
| `pytest/test_display.py` | parser 0–999, API, WebSocket cache |

## Risks / Trade-offs

- **[Risk] `delay(2)` in `showDigit()` slows button response** → Acceptable; `update()` called every loop, buttons read between digit cycles
- **[Risk] Button bounce causes double increment** → 50 ms debounce per button (proven in simple01)
- **[Trade-off] Pin assignment assumed D2/D3/D5** → Document in sketch; user can rewire via `#define` constants

## Migration Plan

1. Add `display_math.h`, button counter logic, rename sketch
2. Add serial protocol
3. Backend parser + API + WebSocket
4. Frontend `/display` page + nav
5. Tests + `AGENTS.md` update

No rollback concerns — additive change.
