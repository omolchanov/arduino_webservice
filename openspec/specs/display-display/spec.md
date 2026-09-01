# display-display Specification

## Purpose

Drive a 3-digit 7-segment counter (000–999) with three physical buttons on Arduino, report the value over serial, and provide a Mulie Board browser dashboard to monitor the live value read from the device.

## Requirements

### Requirement: One sketch per page for display

The Mulie Board dashboard SHALL be driven exclusively by the dedicated firmware in `arduino/mulie_function/`. The system SHALL NOT require or support combining this sketch with keypad, sensors, valves, or simple01 firmware in a single upload.

#### Scenario: User runs Mulie Board dashboard

- **WHEN** the user wants to view the 7-segment display on the Mulie Board dashboard
- **THEN** the user uploads the `arduino/mulie_function/` sketch to the Arduino (not other production sketches)

### Requirement: Three-button digit counter on boot

The firmware SHALL initialize the displayed value to **000** (numeric value `0`) on boot. Three buttons wired with `INPUT_PULLUP` (active LOW on press) SHALL each increment one digit independently:

| Button | Pin | Digit position | Range | Wrap |
|--------|-----|---------------|-------|------|
| Left | A1 | Hundreds (leftmost) | 0–9 | 9 → 0 |
| Middle | A2 | Tens | 0–9 | 9 → 0 |
| Right | A3 | Ones (rightmost) | 0–9 | 9 → 0 |

The fourth display digit SHALL remain `0`. Button presses SHALL be debounced (≥ 50 ms) to avoid multiple increments per press.

#### Scenario: Boot shows 000

- **WHEN** the Arduino resets or powers on
- **THEN** the 7-segment display shows `000`

#### Scenario: Left button increments hundreds digit

- **WHEN** the display shows `005` and the user presses the left button once
- **THEN** the display shows `105`

#### Scenario: Digit wraps from 9 to 0

- **WHEN** the display shows `900` and the user presses the left button once
- **THEN** the display shows `000`

#### Scenario: Middle button increments tens digit

- **WHEN** the display shows `010` and the user presses the middle button once
- **THEN** the display shows `020`

#### Scenario: Right button increments ones digit

- **WHEN** the display shows `007` and the user presses the right button once
- **THEN** the display shows `008`

### Requirement: Display value serial ingestion

The system SHALL read display value lines from an Arduino Uno over USB serial at 9600 baud. Lines matching `Display: <n>` where `<n>` is an integer 0–999 SHALL be parsed and broadcast to all connected WebSocket clients as JSON `{"type": "display", "value": <n>}`.

#### Scenario: Display value line received

- **WHEN** the Arduino sends `Display: 123\n` over serial
- **THEN** the server broadcasts `{"type": "display", "value": 123}` to all connected WebSocket clients

#### Scenario: Display zero value received

- **WHEN** the Arduino sends `Display: 0\n` over serial
- **THEN** the server broadcasts `{"type": "display", "value": 0}` to all connected WebSocket clients

#### Scenario: Invalid display line ignored

- **WHEN** the serial port sends a line that does not match the display format
- **THEN** the server does not broadcast a display event (may still parse as keypad, sensor, or other formats if applicable)

### Requirement: Display value in status API

`GET /api/status` SHALL include `display_value` as an integer 0–999 or `null` when no reading has been received.

#### Scenario: Status includes last display value

- **WHEN** a client requests `GET /api/status` after a display line has been parsed
- **THEN** the response includes `"display_value": <0-999>`

### Requirement: Mulie Board dashboard page

The system SHALL serve a Mulie Board dashboard at `GET /mulie` from `static/mulie.html`. The page SHALL reuse the same visual patterns as existing dashboards (sidebar navigation, dark theme, card layout, online/offline status badge, custom toast notifications).

#### Scenario: Mulie Board page loads

- **WHEN** a user navigates to `/mulie`
- **THEN** the browser displays the Mulie Board dashboard with sidebar navigation including links to Keypad, Sensors, Digital Signal, Valves, and Mulie Board

### Requirement: Display value widget

The Mulie Board dashboard SHALL include a read-only live widget showing the current 3-digit value (000–999, zero-padded) **as reported by the board** over serial. The widget SHALL update whenever the firmware sends `Display: <n>`—including after physical button presses or an on-device reset.

#### Scenario: Widget reflects board button input

- **WHEN** the user presses buttons on the mulie function board so the 7-segment display shows `105` and the Arduino sends `Display: 105\n`
- **THEN** the Mulie Board widget updates to show `105` without any browser action

#### Scenario: Widget updates on WebSocket display event

- **WHEN** the page receives a WebSocket `display` event with `"value": 42`
- **THEN** the widget updates to show `042`

#### Scenario: Widget shows cached value on page load

- **WHEN** a user opens `/mulie` and `GET /api/status` returns `"display_value": 237` (or the WebSocket sends a cached `display` event)
- **THEN** the widget shows `237` before any new button press

### Requirement: WebSocket cached display value on connect

When a WebSocket client connects, the server SHALL send the last known display value if available, with `"cached": true`, using the same pattern as logic and valve readings.

#### Scenario: New client receives cached display value

- **WHEN** a WebSocket client connects and a display value has previously been parsed
- **THEN** the server sends `{"type": "display", "value": <n>, "cached": true}` before any new serial data arrives
