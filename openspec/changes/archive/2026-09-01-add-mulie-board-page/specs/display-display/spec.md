## MODIFIED Requirements

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

### Requirement: Mulie Board dashboard page

The system SHALL serve a Mulie Board dashboard at `GET /mulie` from `static/mulie.html`. The page SHALL reuse the same visual patterns as existing dashboards (sidebar navigation, dark theme, card layout, online/offline status badge, custom toast notifications).

#### Scenario: Mulie Board page loads

- **WHEN** a user navigates to `/mulie`
- **THEN** the browser displays the Mulie Board dashboard with sidebar navigation including links to Keypad, Sensors, Digital Signal, Valves, and Mulie Board

### Requirement: Display value widget

The Mulie Board dashboard SHALL include a read-only live widget showing the current 3-digit value (000–999, zero-padded) **as reported by the board** over serial. The widget SHALL update whenever the firmware sends `Display: <n>`—including after physical button presses or an on-device reset—not only after remote Set/Reset commands. The page SHALL also provide a numeric input with a Set button (`POST /api/display/value`) and a Reset button (`POST /api/display/reset`) for remote control.

#### Scenario: Widget reflects board button input

- **WHEN** the user presses buttons on the mulie function board so the 7-segment display shows `105` and the Arduino sends `Display: 105\n`
- **THEN** the Mulie Board widget updates to show `105` without any browser action

#### Scenario: Widget updates on WebSocket display event

- **WHEN** the page receives a WebSocket `display` event with `"value": 42`
- **THEN** the widget updates to show `042`

#### Scenario: Widget shows cached value on page load

- **WHEN** a user opens `/mulie` and `GET /api/status` returns `"display_value": 237` (or the WebSocket sends a cached `display` event)
- **THEN** the widget shows `237` before any new button press

#### Scenario: User sets a new value

- **WHEN** the user enters `999` and clicks Set
- **THEN** the page sends `POST /api/display/value` with `{"value": 999}` and shows a success or error toast notification

#### Scenario: User resets the counter

- **WHEN** the user clicks Reset
- **THEN** the page sends `POST /api/display/reset` and shows a success or error toast notification

## ADDED Requirements

### Requirement: Reset display API

The system SHALL provide `POST /api/display/reset` with no request body. On success the server SHALL send `RESET\n` to the Arduino over serial and return `{"ok": true}`.

#### Scenario: Reset sent to Arduino

- **WHEN** a client sends `POST /api/display/reset` and serial is connected
- **THEN** the server writes `RESET\n` to the serial port and returns `{"ok": true}`

#### Scenario: Serial disconnected on reset

- **WHEN** a client sends `POST /api/display/reset` and the serial port is not connected
- **THEN** the server returns HTTP 503

## REMOVED Requirements

### Requirement: Display dashboard page

**Reason**: Replaced by the Mulie Board dashboard with clearer naming aligned to the `mulie_function` sketch.

**Migration**: Use `GET /mulie` instead of `GET /display`. Update bookmarks and nav links accordingly.
