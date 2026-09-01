# display-display Specification

## Purpose

Drive a 3-digit 7-segment counter (000–999) with three physical buttons on Arduino, report the value over serial, and provide a browser dashboard to monitor and set the displayed number remotely.

## Requirements

### Requirement: One sketch per page for display

The Display dashboard SHALL be driven exclusively by the dedicated firmware in `arduino/mulie_function/`. The system SHALL NOT require or support combining this sketch with keypad, sensors, valves, or simple01 firmware in a single upload.

#### Scenario: User runs display dashboard

- **WHEN** the user wants to view or control the 7-segment display on the Display dashboard
- **THEN** the user uploads the `arduino/mulie_function/` sketch to the Arduino (not other production sketches)

### Requirement: Three-button digit counter on boot

The firmware SHALL initialize the displayed value to **000** (numeric value `0`) on boot. Three buttons wired with `INPUT_PULLUP` (active LOW on press) SHALL each increment one digit independently:

| Button | Digit position | Range | Wrap |
|--------|---------------|-------|------|
| Left (D2) | Hundreds (leftmost) | 0–9 | 9 → 0 |
| Middle (D3) | Tens | 0–9 | 9 → 0 |
| Right (D5) | Ones (rightmost) | 0–9 | 9 → 0 |

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

### Requirement: Set display value API

The system SHALL provide `POST /api/display/value` accepting JSON `{"value": <n>}` where `<n>` is an integer 0–999. On success the server SHALL send `S<n>\n` to the Arduino over serial and return `{"ok": true, "value": <n>}`.

#### Scenario: Valid value sent to Arduino

- **WHEN** a client sends `POST /api/display/value` with body `{"value": 567}` and serial is connected
- **THEN** the server writes `S567\n` to the serial port and returns `{"ok": true, "value": 567}`

#### Scenario: Invalid value rejected

- **WHEN** a client sends `POST /api/display/value` with a value outside 0–999
- **THEN** the server returns HTTP 400 with an error message

#### Scenario: Serial disconnected

- **WHEN** a client sends `POST /api/display/value` and the serial port is not connected
- **THEN** the server returns HTTP 503

### Requirement: Display dashboard page

The system SHALL serve a Display dashboard at `GET /display` from `static/display.html`. The page SHALL reuse the same visual patterns as existing dashboards (sidebar navigation, dark theme, card layout, online/offline status badge, custom toast notifications).

#### Scenario: Display page loads

- **WHEN** a user navigates to `/display`
- **THEN** the browser displays the Display dashboard with sidebar navigation including links to Keypad, Sensors, Digital Signal, Valves, and Display

### Requirement: Display value widget

The Display dashboard SHALL include a widget showing the current 3-digit display value (000–999, zero-padded) and a numeric input with a Set button to send a new value via `POST /api/display/value`.

#### Scenario: Widget updates on new display value

- **WHEN** the page receives a WebSocket `display` event with `"value": 42`
- **THEN** the widget updates to show `042`

#### Scenario: User sets a new value

- **WHEN** the user enters `999` and clicks Set
- **THEN** the page sends `POST /api/display/value` with `{"value": 999}` and shows a success or error toast notification

### Requirement: WebSocket cached display value on connect

When a WebSocket client connects, the server SHALL send the last known display value if available, with `"cached": true`, using the same pattern as logic and valve readings.

#### Scenario: New client receives cached display value

- **WHEN** a WebSocket client connects and a display value has previously been parsed
- **THEN** the server sends `{"type": "display", "value": <n>, "cached": true}` before any new serial data arrives
