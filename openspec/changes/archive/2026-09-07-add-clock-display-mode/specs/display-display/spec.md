## ADDED Requirements

### Requirement: Dual display mode counter and clock

The `arduino/mulie_function/` firmware SHALL support two display modes:

| Mode | Display | Button behavior |
|------|---------|-----------------|
| Counter | 3-digit counter `000`–`999` (leading digit `0`) | Left/middle/right buttons increment hundreds/tens/ones as today |
| Clock | 24-hour time `hh:mm` with a colon dot between hours and minutes | Individual digit buttons SHALL have no effect |

The firmware SHALL boot in **counter** mode showing `000`.

#### Scenario: Boot in counter mode

- **WHEN** the Arduino resets or powers on
- **THEN** the display shows `000` and individual buttons increment digits

#### Scenario: Clock mode shows hh:mm with colon

- **WHEN** the firmware is in clock mode and the internal time is 12:00
- **THEN** the display shows `12` colon `00` (four digits: hour tens, hour ones, minute tens, minute ones, with a visible dot between the hour and minute pairs)

#### Scenario: Clock mode ignores digit buttons

- **WHEN** the firmware is in clock mode and the user presses left, middle, or right button individually
- **THEN** the displayed time does not change

### Requirement: Mode toggle via reset button long hold

Pressing the dedicated **reset button** (wired active LOW on A1–A3 together) for **≥ 3000 ms** SHALL toggle between counter mode and clock mode exactly once per hold. A distinct feedback beep SHALL indicate the mode change.

#### Scenario: Switch from counter to clock

- **WHEN** the firmware is in counter mode and the user holds the reset button for at least 3 seconds
- **THEN** the display switches to clock mode showing the current internal time in `hh:mm` format

#### Scenario: Switch from clock to counter

- **WHEN** the firmware is in clock mode and the user holds the reset button for at least 3 seconds
- **THEN** the display switches to counter mode showing the last counter value (unchanged while clock was visible)

#### Scenario: Hold under 3 seconds does not toggle mode

- **WHEN** the user holds the reset button for less than 3 seconds and releases
- **THEN** the display mode does not change

### Requirement: Background clock from 12:00

The firmware SHALL maintain an internal 24-hour clock starting at **12:00** (720 minutes since midnight) on first boot. The clock SHALL advance one minute every 60 seconds of real time regardless of which display mode is active.

#### Scenario: Clock starts at 12:00

- **WHEN** the Arduino powers on and the user toggles to clock mode before one minute elapses
- **THEN** the display shows `12:00`

#### Scenario: Clock advances in background while counter shown

- **WHEN** the firmware is in counter mode and at least one minute passes since the last clock tick
- **THEN** the internal time advances by one minute
- **AND WHEN** the user later toggles to clock mode
- **THEN** the display shows the updated time (not still 12:00 unless no minute has passed)

#### Scenario: Clock wraps at midnight

- **WHEN** the internal time is 23:59 and one minute passes
- **THEN** the internal time becomes 00:00

### Requirement: Short hold reset preserved in counter mode

In **counter mode only**, holding the **reset button** for **≥ 500 ms** and releasing **before 3000 ms** SHALL reset the counter to `000`, preserving existing reset behavior without triggering a mode toggle.

#### Scenario: Short hold resets counter

- **WHEN** the firmware is in counter mode, the display shows `456`, and the user holds the reset button for at least 500 ms but less than 3 seconds then releases
- **THEN** the display shows `000` and remains in counter mode

#### Scenario: Short hold does not reset in clock mode

- **WHEN** the firmware is in clock mode and the user holds the reset button for 500 ms to 2999 ms then releases
- **THEN** the displayed time is unchanged and the firmware remains in clock mode

### Requirement: Clock time serial ingestion

The system SHALL read clock lines from an Arduino Uno over USB serial at 9600 baud. Lines matching `Clock: HH:MM` where `HH` is 00–23 and `MM` is 00–59 SHALL be parsed and broadcast to all connected WebSocket clients as JSON `{"type": "clock", "time": "HH:MM"}`. The firmware SHALL emit `Clock: HH:MM` on boot with the initial time (12:00) and after each internal minute tick regardless of display mode.

#### Scenario: Clock line received on boot

- **WHEN** the Arduino sends `Clock: 12:00\n` over serial
- **THEN** the server broadcasts `{"type": "clock", "time": "12:00"}` to all connected WebSocket clients

#### Scenario: Clock line after minute tick in counter mode

- **WHEN** the firmware is in counter mode on the physical display and sends `Clock: 12:01\n` after a background minute tick
- **THEN** the server broadcasts `{"type": "clock", "time": "12:01"}` without changing the counter widget value

#### Scenario: Invalid clock line ignored

- **WHEN** the serial port sends `Clock: 25:00\n` or a line that does not match the clock format
- **THEN** the server does not broadcast a clock event

### Requirement: Clock time in status API

`GET /api/status` SHALL include `clock_time` as a string `HH:MM` or `null` when no clock reading has been received.

#### Scenario: Status includes last clock time

- **WHEN** a client requests `GET /api/status` after a clock line has been parsed
- **THEN** the response includes `"clock_time": "12:00"` (or the last parsed time)

### Requirement: Clock dashboard widget

The Display dashboard at `GET /display` SHALL include a **separate** read-only widget showing the current clock time in `HH:MM` format, distinct from the existing counter widget. The clock widget SHALL update from WebSocket `clock` events and from `clock_time` on initial status poll. It SHALL reuse the same card layout and live status dot pattern as the counter widget.

#### Scenario: Clock widget shows live time

- **WHEN** the page receives a WebSocket `clock` event with `"time": "14:30"`
- **THEN** the clock widget displays `14:30` and its status dot indicates a live reading

#### Scenario: Clock and counter widgets are independent

- **WHEN** a user loads the Display dashboard
- **THEN** the page shows both the counter value widget (000–999) and a distinct clock widget (hh:mm)

#### Scenario: Counter and clock values update independently

- **WHEN** the page receives a WebSocket `display` event with `"value": 42` and a `clock` event with `"time": "12:05"`
- **THEN** the counter widget shows `042` and the clock widget shows `12:05`

### Requirement: WebSocket cached clock time on connect

When a WebSocket client connects, the server SHALL send the last known clock time if available, with `"cached": true`, using the same pattern as display and valve readings.

#### Scenario: New client receives cached clock time

- **WHEN** a WebSocket client connects and a clock time has previously been parsed
- **THEN** the server sends `{"type": "clock", "time": "12:00", "cached": true}` before any new serial data arrives
