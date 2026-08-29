## ADDED Requirements

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

## MODIFIED Requirements

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
