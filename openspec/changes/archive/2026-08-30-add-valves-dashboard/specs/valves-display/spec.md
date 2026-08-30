## Purpose

Read logical valve state (AND/OR gates with inputs A, B and output Y) from a dedicated Arduino sketch over USB serial, allow gate selection via API, and display live values with a truth table on a Valves dashboard.

## ADDED Requirements

### Requirement: One sketch per Valves dashboard

The Valves dashboard SHALL be driven exclusively by the dedicated firmware at `arduino/valves.ino`. The system SHALL NOT require or support combining this dashboard with other sensor or keypad sketches in a single firmware upload.

#### Scenario: User runs Valves dashboard

- **WHEN** the user wants to view the Valves dashboard at `/valves`
- **THEN** the user uploads `arduino/valves.ino` to the Arduino (not `sensors.ino`, `simple01.ino`, or keypad firmware)

### Requirement: Valve status serial ingestion

The system SHALL read valve status lines from `arduino/valves.ino` over USB serial at 9600 baud. Lines matching `A = <0|1> | B = <0|1> | Y = <0|1> | Gate = AND` or `Gate = OR` SHALL be parsed and broadcast to all connected WebSocket clients as JSON `{"type": "valve", "a": <0|1>, "b": <0|1>, "y": <0|1>, "gate": "AND"|"OR"}`.

#### Scenario: AND gate status line received

- **WHEN** the Arduino sends `A = 0 | B = 1 | Y = 0 | Gate = AND` over serial
- **THEN** the server broadcasts `{"type": "valve", "a": 0, "b": 1, "y": 0, "gate": "AND"}` to all connected WebSocket clients

#### Scenario: OR gate status line received

- **WHEN** the Arduino sends `A = 1 | B = 1 | Y = 1 | Gate = OR` over serial
- **THEN** the server broadcasts `{"type": "valve", "a": 1, "b": 1, "y": 1, "gate": "OR"}` to all connected WebSocket clients

#### Scenario: Invalid valve line ignored

- **WHEN** the serial port sends a line that does not match the valve status format
- **THEN** the server does not broadcast a valve event (may still parse as distance, light, pot, or keypad if applicable)

### Requirement: Valve values in status API

`GET /api/status` SHALL include `last_valve_a`, `last_valve_b`, and `last_valve_y` as integers `0`, `1`, or `null` when no reading has been received. It SHALL also include `last_valve_gate` as the string `"AND"`, `"OR"`, or `null`.

#### Scenario: Status includes last valve values

- **WHEN** a client requests `GET /api/status` after a valve status line has been parsed
- **THEN** the response includes `"last_valve_a": 0`, `"last_valve_b": 1`, `"last_valve_y": 0`, and `"last_valve_gate": "AND"` (or corresponding values from the last reading)

### Requirement: Gate selection API

The system SHALL expose `POST /api/valve/gate` accepting JSON `{"gate": "AND" | "OR"}`. When serial is connected, the server SHALL write `A` to the serial port for AND or `O` for OR. The endpoint SHALL return 400 for an invalid gate value and 503 when serial is disconnected.

#### Scenario: Select AND gate

- **WHEN** a client sends `POST /api/valve/gate` with body `{"gate": "AND"}` and serial is connected
- **THEN** the server writes `A` to the serial port and returns `{"ok": true, "gate": "AND"}`

#### Scenario: Select OR gate

- **WHEN** a client sends `POST /api/valve/gate` with body `{"gate": "OR"}` and serial is connected
- **THEN** the server writes `O` to the serial port and returns `{"ok": true, "gate": "OR"}`

#### Scenario: Gate selection when serial disconnected

- **WHEN** a client sends `POST /api/valve/gate` and serial is not connected
- **THEN** the server returns HTTP 503

### Requirement: Valves dashboard page

The system SHALL serve a Valves dashboard at `GET /valves` from `static/valves.html`. The page SHALL reuse the same visual patterns as the Digital Signal dashboard (sidebar navigation, dark theme, card layout, online/offline status badge, custom toast notifications).

#### Scenario: Valves page loads

- **WHEN** a user navigates to `/valves`
- **THEN** the browser displays the Valves dashboard with sidebar navigation including links to Keypad, Sensors, Digital Signal, and Valves

### Requirement: Gate selection dropdown

The Valves dashboard SHALL include a dropdown in the top-right area (left of the connection status badge) allowing the user to select AND or OR. Changing the selection SHALL call `POST /api/valve/gate` and SHALL show a custom toast notification on success or error (not a browser alert).

#### Scenario: User selects OR from dropdown

- **WHEN** the user changes the dropdown from AND to OR
- **THEN** the page sends `POST /api/valve/gate` with `{"gate": "OR"}` and shows a success or error toast

### Requirement: Selected gate widget

The Valves dashboard SHALL include a widget displaying the currently reported gate (`AND` or `OR`) from live serial data. The widget SHALL include a status dot following the same online/offline and pending-reading pattern as widgets on the Digital Signal dashboard.

#### Scenario: Gate widget updates on new reading

- **WHEN** the page receives a WebSocket `valve` event with `"gate": "OR"`
- **THEN** the selected gate widget displays `OR` and the status dot shows ok

### Requirement: Inputs widget

The Valves dashboard SHALL include a widget displaying input values A and B from live serial data. The widget SHALL include a status dot following the same online/offline and pending-reading pattern as widgets on the Digital Signal dashboard.

#### Scenario: Inputs widget updates on new reading

- **WHEN** the page receives a WebSocket `valve` event with `"a": 1` and `"b": 0`
- **THEN** the inputs widget displays A as `1` and B as `0`

### Requirement: Output widget

The Valves dashboard SHALL include a widget displaying output value Y from live serial data. The widget SHALL include a status dot following the same online/offline and pending-reading pattern as widgets on the Digital Signal dashboard.

#### Scenario: Output widget updates on new reading

- **WHEN** the page receives a WebSocket `valve` event with `"y": 1`
- **THEN** the output widget displays `1`

### Requirement: Truth table

The Valves dashboard SHALL display a truth table below the widgets with columns A, B, and Y. The Y column SHALL show correct values for the selected gate: AND (0,0→0; 0,1→0; 1,0→0; 1,1→1) and OR (0,0→0; 0,1→1; 1,0→1; 1,1→1). The row matching the current live A and B values SHALL be visually highlighted.

#### Scenario: Truth table highlights current inputs for AND

- **WHEN** the selected gate is AND and live inputs are A=1, B=0
- **THEN** the truth table row for A=1, B=0 is highlighted and shows Y=0

#### Scenario: Truth table updates when gate changes

- **WHEN** the user changes the dropdown from AND to OR
- **THEN** the truth table Y column updates to OR logic while row highlight still follows live A and B

### Requirement: WebSocket cached valve state on connect

When a WebSocket client connects, the server SHALL send the last known valve state (if available) with `"cached": true`, using the same pattern as distance and light cached messages.

#### Scenario: Connect receives cached valve state

- **WHEN** a client connects to `/ws` after a valve status line has been parsed
- **THEN** the client receives `{"type": "valve", "a": <n>, "b": <n>, "y": <n>, "gate": "<gate>", "cached": true}`

### Requirement: Valves navigation link

All dashboard pages (Keypad, Sensors, Digital Signal, Valves) SHALL include a sidebar link to `/valves` labeled **Valves**.

#### Scenario: Nav link on Keypad page

- **WHEN** a user views the Keypad page at `/`
- **THEN** the sidebar includes a link to `/valves`
