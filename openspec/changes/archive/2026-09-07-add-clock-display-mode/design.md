## Context

See `proposal.md`. The `mulie_function` sketch drives a 4-digit 7-segment display via `MultiFunctionDisplay`. Counter mode uses digit positions 1–3 (left pad 0). All three buttons pressed together currently triggers reset after 500 ms. There is no colon segment support and no timekeeping logic.

## Goals / Non-Goals

**Goals:**

- Two runtime modes: counter (existing) and clock (`hh:mm` with colon dot).
- Toggle modes with a 3-second all-buttons hold; preserve short-hold reset in counter mode.
- Clock starts at 12:00, advances every real minute, and keeps running while counter mode is active.
- Testable clock math in `display_math.h` (EpoxyDuino); minimal firmware changes elsewhere.
- Display dashboard shows clock time in a **separate widget** from the counter, updated live over WebSocket.

**Non-Goals:**

- Setting time via buttons, serial, or the web UI; alarm; 12/24-hour user setting.
- RTC hardware or NTP—time is software-only from boot.

## Decisions

### 1. Mode toggle vs short reset on the same gesture

**Decision:** Single all-buttons gesture with duration thresholds:

| Hold duration | Action (counter mode) | Action (clock mode) |
|---------------|----------------------|---------------------|
| ≥ 3000 ms | Toggle to clock mode (once per hold) | Toggle to counter mode (once per hold) |
| ≥ 500 ms and release before 3000 ms | Reset counter to 000 | No reset |
| < 500 ms | No action | No action |

Mode toggle fires at the 3000 ms mark (no need to release). Short reset fires on release if hold was 500–2999 ms. This avoids resetting at 500 ms while the user is still holding for mode switch.

**Alternative considered:** Separate reset at 500 ms while holding—rejected because a 3 s hold would reset the counter mid-gesture.

### 2. Background clock with `millis()`

**Decision:** Maintain `clockMinutes` (0–1439, minutes since midnight) and `lastClockTickMs`. On each `loop()` iteration, if `millis() - lastClockTickMs >= 60000`, increment minutes (wrap 1439 → 0). Initialize to 720 (12:00) on first boot.

Clock math runs unconditionally in `loop()` regardless of active display mode.

**Alternative considered:** Only tick while in clock mode—rejected; user requires background advancement.

### 3. Display layout for `hh:mm`

**Decision:** Map the four digit positions as:

| Index | Content |
|-------|---------|
| 0 | Hour tens |
| 1 | Hour ones |
| 2 | Minute tens |
| 3 | Minute ones |

Render a colon segment (segment pattern `0xBF`, both middle dots) on the minute-tens digit (index 2) during multiplex refresh so the display reads `12·00` style with a dot between hours and minutes.

**Alternative considered:** Blank leading hour digit for times before 10:00—rejected; show `09:05` with leading zero.

### 4. `MultiFunctionDisplay` API

**Decision:** Add `showClock(byte hours, byte minutes)` and a `_clockMode` flag (or separate colon bit per digit). `update()` multiplexes using counter or clock digit buffer. `show(int)` remains for counter mode.

Keep segment map in `.cpp`; add `COLON_SEGMENT` constant OR'd into segment data when rendering digit index 2 in clock mode.

### 5. Serial output

**Decision:**

| Line | When |
|------|------|
| `Display: <n>` | Counter value changes (unchanged) |
| `Clock: HH:MM` | On boot (initial 12:00) and after each minute tick (background or clock mode) |
| `Mode: counter` / `Mode: clock` | On mode toggle |

Python parses `Clock:` with regex `^Clock:\s*(\d{2}):(\d{2})$`, validates 00:00–23:59, stores `last_clock_time` as `"HH:MM"` string, broadcasts `{"type": "clock", "time": "HH:MM"}` on WebSocket. Mode lines update `last_display_mode` (`"counter"` \| `"clock"`) and broadcast `{"type": "display_mode", "mode": "..."}` (optional subtitle on clock widget).

**Alternative considered:** Derive clock time only on the server—rejected; Arduino is source of truth for firmware clock.

### 6. Dashboard clock widget

**Decision:** Add a second card on `static/display.html` beside the existing counter card:

- Header: **Clock** with live status dot (same pattern as counter widget).
- Body: large `hh:mm` value (colon between hours and minutes, tabular nums, reuse `.display-value` styling).
- Subtitle: `internal clock (24h)` — no set control (read-only).
- WebSocket handler for `type === "clock"`; `GET /api/status` field `clock_time` for poll/cache on connect.

Counter widget remains unchanged (000–999 + Set).

**Alternative considered:** Single combined widget—rejected per user request for a separate clock widget.

### 7. Button handling in clock mode

**Decision:** Individual button presses are ignored in clock mode (no digit increments). Only the all-buttons gesture toggles mode or does nothing (no reset in clock mode).

## Risks / Trade-offs

- **[Drift]** `millis()`-based minutes drift vs wall clock → acceptable for demo firmware; document in comments.
- **[Colon wiring]** Colon segment pattern may need tuning per display module → verify on hardware; unit tests cover digit splitting only.
- **[Hold UX]** Users may accidentally reset when aiming for mode toggle → 500 ms–3 s window is intentional; double beep on mode toggle for feedback.

## Migration Plan

1. Upload updated `mulie_function` sketch.
2. Boot defaults to counter mode (000); clock starts at 12:00 internally.
3. Hold all three buttons 3 s to switch to clock; hold again 3 s to return.
4. Rollback: re-flash previous sketch.
