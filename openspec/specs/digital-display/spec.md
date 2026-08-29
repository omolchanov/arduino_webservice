# digital-display Specification

## Purpose
Read digital logic levels (0 and 1) from a dedicated Arduino sketch over USB serial and display them on a separate Digital Signal dashboard with a live graph widget.

## Requirements

### Requirement: One sketch per widget for logic signal

The logic signal graph widget SHALL be driven exclusively by the dedicated firmware at `arduino/simple01.ino`. The system SHALL NOT require or support combining this widget with other sensor or keypad sketches in a single firmware upload.

#### Scenario: User runs logic graph widget

- **WHEN** the user wants to view the logic signal graph on the Digital Signal dashboard
- **THEN** the user uploads `arduino/simple01.ino` to the Arduino (not `sensors.ino` or keypad firmware)

### Requirement: Logic signal serial ingestion

The system SHALL read digital logic measurements from an Arduino Uno over USB serial at 9600 baud. Lines from `arduino/simple01.ino` that include `Generated: 0` or `Generated: 1` (e.g. `Generated: 1 | Potentiometer: 2.50 V | Detected: 1`) SHALL be parsed and broadcast to all connected WebSocket clients as JSON `{"type": "logic", "value": <0|1>}`. Only the generated logic value is required for the graph widget.

#### Scenario: Logic HIGH line received

- **WHEN** the Arduino sends `Generated: 1 | Potentiometer: 2.50 V | Detected: 1\n` over serial
- **THEN** the server broadcasts `{"type": "logic", "value": 1}` to all connected WebSocket clients

#### Scenario: Logic LOW line received

- **WHEN** the Arduino sends `Generated: 0 | Potentiometer: 1.20 V | Detected: 0\n` over serial
- **THEN** the server broadcasts `{"type": "logic", "value": 0}` to all connected WebSocket clients

#### Scenario: Invalid logic line ignored

- **WHEN** the serial port sends a line that does not match the logic format
- **THEN** the server does not broadcast a logic event (may still parse as distance, light, or keypad if applicable)

### Requirement: Logic value in status API

`GET /api/status` SHALL include `last_logic_value` as an integer `0`, `1`, or `null` when no reading has been received. It SHALL also include `last_potentiometer_v` as a float or `null` and `last_detected_value` as an integer `0`, `1`, or `null` when no reading has been received.

#### Scenario: Status includes last logic value

- **WHEN** a client requests `GET /api/status` after a logic line has been parsed
- **THEN** the response includes `"last_logic_value": 0` or `"last_logic_value": 1`

#### Scenario: Status includes last potentiometer voltage

- **WHEN** a client requests `GET /api/status` after a `simple01.ino` line with potentiometer data has been parsed
- **THEN** the response includes `"last_potentiometer_v"` as a float (e.g. `2.5`)

#### Scenario: Status includes last detected value

- **WHEN** a client requests `GET /api/status` after a `simple01.ino` line with detected data has been parsed
- **THEN** the response includes `"last_detected_value": 0` or `"last_detected_value": 1`

### Requirement: Digital Signal dashboard page

The system SHALL serve a Digital Signal dashboard at `GET /digital` from `static/digital.html`. The page SHALL reuse the same visual patterns as the Sensors dashboard (sidebar navigation, dark theme, card layout, online/offline status badge, custom toast notifications).

#### Scenario: Digital page loads

- **WHEN** a user navigates to `/digital`
- **THEN** the browser displays the Digital Signal dashboard with sidebar navigation including links to Keypad, Sensors, and Digital Signal

### Requirement: Logic signal graph widget

The Digital Signal dashboard SHALL include a logic signal graph widget that displays live 0/1 values over time as a stepped line chart with a rolling client-side history buffer.

#### Scenario: Graph updates on new logic value

- **WHEN** the page receives a WebSocket `logic` event with `"value": 1` or `"value": 0`
- **THEN** the graph appends the new point and updates the display to show the current logic level

#### Scenario: Graph shows only 0 and 1 on Y-axis

- **WHEN** the logic signal graph is rendered
- **THEN** the Y-axis displays only values 0 and 1

### Requirement: WebSocket cached logic value on connect

When a WebSocket client connects, the server SHALL send the last known logic value if available, with `"cached": true`, using the same pattern as distance and light readings.

#### Scenario: New client receives cached logic value

- **WHEN** a WebSocket client connects and a logic value has previously been parsed
- **THEN** the server sends `{"type": "logic", "value": <0|1>, "cached": true}` before any new serial data arrives

### Requirement: Potentiometer serial ingestion

The system SHALL read potentiometer voltage from `arduino/simple01.ino` serial lines at 9600 baud. Lines matching the full format (e.g. `Generated: 1 | Potentiometer: 2.50 V | Detected: 1`) SHALL be parsed and the potentiometer field SHALL be broadcast to all connected WebSocket clients as JSON `{"type": "potentiometer", "v": <float>}`.

#### Scenario: Potentiometer line received

- **WHEN** the Arduino sends `Generated: 1 | Potentiometer: 2.50 V | Detected: 1\n` over serial
- **THEN** the server broadcasts `{"type": "potentiometer", "v": 2.5}` to all connected WebSocket clients

#### Scenario: Invalid potentiometer line ignored

- **WHEN** the serial port sends a line that does not match the full `simple01.ino` format
- **THEN** the server does not broadcast a potentiometer event

### Requirement: Detected logic serial ingestion

The system SHALL read the detected logic state from `arduino/simple01.ino` serial lines at 9600 baud. Lines matching the full format (e.g. `Generated: 1 | Potentiometer: 2.50 V | Detected: 1`) SHALL be parsed and the detected field SHALL be broadcast to all connected WebSocket clients as JSON `{"type": "detected", "value": <0|1>}`. The detected value reflects the logic state driving the second LED on D9.

#### Scenario: Detected HIGH line received

- **WHEN** the Arduino sends `Generated: 0 | Potentiometer: 3.10 V | Detected: 1\n` over serial
- **THEN** the server broadcasts `{"type": "detected", "value": 1}` to all connected WebSocket clients

#### Scenario: Detected LOW line received

- **WHEN** the Arduino sends `Generated: 1 | Potentiometer: 1.20 V | Detected: 0\n` over serial
- **THEN** the server broadcasts `{"type": "detected", "value": 0}` to all connected WebSocket clients

### Requirement: Potentiometer voltage widget

The Digital Signal dashboard SHALL include a potentiometer widget that displays the live voltage reading from the potentiometer field in volts, formatted to two decimal places with a `V` unit label. The widget SHALL include a status dot that follows the same online/offline and pending-reading pattern as sensor widgets on the Sensors dashboard.

#### Scenario: Potentiometer widget updates on new reading

- **WHEN** the page receives a WebSocket `potentiometer` event with `"v": 2.5`
- **THEN** the potentiometer widget displays `2.50` with unit `V`

#### Scenario: Potentiometer widget seeds from status API

- **WHEN** a user loads `/digital` and `GET /api/status` returns `"last_potentiometer_v": 1.85`
- **THEN** the potentiometer widget displays `1.85` before any new serial data arrives

### Requirement: Detected logic LED widget

The Digital Signal dashboard SHALL include a detected logic LED widget that displays the live detected logic state as `0` or `1`, representing the state of the second LED on D9. The widget SHALL include a status dot that follows the same online/offline and pending-reading pattern as sensor widgets on the Sensors dashboard.

#### Scenario: Detected widget updates on new reading

- **WHEN** the page receives a WebSocket `detected` event with `"value": 1`
- **THEN** the detected logic LED widget displays `1`

#### Scenario: Detected widget seeds from status API

- **WHEN** a user loads `/digital` and `GET /api/status` returns `"last_detected_value": 0`
- **THEN** the detected logic LED widget displays `0` before any new serial data arrives

### Requirement: WebSocket cached potentiometer and detected values on connect

When a WebSocket client connects, the server SHALL send the last known potentiometer voltage and detected logic value if available, each with `"cached": true`, using the same pattern as logic, distance, and light readings.

#### Scenario: New client receives cached potentiometer value

- **WHEN** a WebSocket client connects and a potentiometer reading has previously been parsed
- **THEN** the server sends `{"type": "potentiometer", "v": <float>, "cached": true}` before any new serial data arrives

#### Scenario: New client receives cached detected value

- **WHEN** a WebSocket client connects and a detected logic value has previously been parsed
- **THEN** the server sends `{"type": "detected", "value": <0|1>, "cached": true}` before any new serial data arrives
