## MODIFIED Requirements

### Requirement: Logic value in status API

`GET /api/status` SHALL include `last_logic_value` as an integer `0`, `1`, or `null` when no reading has been received. It SHALL also include `last_potentiometer_v` as a float or `null`, `last_detected_value` as `0`, `0.5`, `1`, or `null` when no reading has been received, and `last_current_ma` as a float or `null` when no current reading has been received. The value `0.5` represents the undefined pot logic zone.

#### Scenario: Status includes last logic value

- **WHEN** a client requests `GET /api/status` after a SIGNAL_PIN logic line has been parsed
- **THEN** the response includes `"last_logic_value": 0` or `"last_logic_value": 1`

#### Scenario: Status includes last potentiometer voltage

- **WHEN** a client requests `GET /api/status` after a `Pot:` line has been parsed
- **THEN** the response includes `"last_potentiometer_v"` as a float (e.g. `2.5`)

#### Scenario: Status includes last detected value

- **WHEN** a client requests `GET /api/status` after a `Pot:` line with logic data has been parsed
- **THEN** the response includes `"last_detected_value": 0`, `"last_detected_value": 0.5`, or `"last_detected_value": 1`

#### Scenario: Status includes last current value

- **WHEN** a client requests `GET /api/status` after a `Pot:` line with a `Current:` field has been parsed
- **THEN** the response includes `"last_current_ma"` as a float (e.g. `12.3`)

### Requirement: Potentiometer serial ingestion

The system SHALL read potentiometer voltage from `arduino/simple01.ino` serial lines at 9600 baud. Lines matching `Pot: <voltage> V | Logic: <state>` with optional `| PWM: <n>`, `| Shunt: <voltage> V`, and `| Current: <mA> mA` suffixes SHALL be parsed and the voltage field SHALL be broadcast to all connected WebSocket clients as JSON `{"type": "potentiometer", "v": <float>}`. Lines without the shunt/current suffixes SHALL remain valid.

#### Scenario: Potentiometer line received

- **WHEN** the Arduino sends `Pot: 2.50 V | Logic: 0\n` over serial
- **THEN** the server broadcasts `{"type": "potentiometer", "v": 2.5}` to all connected WebSocket clients

#### Scenario: Potentiometer line with PWM suffix received

- **WHEN** the Arduino sends `Pot: 4.00 V | Logic: 1 | PWM: 200\n` over serial
- **THEN** the server broadcasts `{"type": "potentiometer", "v": 4.0}` to all connected WebSocket clients

#### Scenario: Potentiometer line with current suffix received

- **WHEN** the Arduino sends `Pot: 4.00 V | Logic: 1 | PWM: 200 | Shunt: 0.123 V | Current: 12.3 mA\n` over serial
- **THEN** the server broadcasts `{"type": "potentiometer", "v": 4.0}` to all connected WebSocket clients

#### Scenario: Invalid potentiometer line ignored

- **WHEN** the serial port sends a line that does not match the `Pot:` format
- **THEN** the server does not broadcast a potentiometer event

## ADDED Requirements

### Requirement: Current serial ingestion

The system SHALL read the current measurement from `arduino/simple01.ino` `Pot:` serial lines at 9600 baud when the line includes a `Current: <mA> mA` field. Each parsed line SHALL broadcast to all connected WebSocket clients as JSON `{"type": "current", "ma": <float>}`. The shunt voltage field SHALL be accepted in the line format but SHALL NOT be broadcast.

#### Scenario: Current line received

- **WHEN** the Arduino sends `Pot: 4.00 V | Logic: 1 | PWM: 200 | Shunt: 0.123 V | Current: 12.3 mA\n` over serial
- **THEN** the server broadcasts `{"type": "current", "ma": 12.3}` to all connected WebSocket clients

#### Scenario: Line without current field does not broadcast current

- **WHEN** the Arduino sends `Pot: 2.50 V | Logic: 0\n` over serial
- **THEN** the server does not broadcast a current event

### Requirement: Current mA widget

The Digital Signal dashboard SHALL include a current widget that displays the live current reading in milliamps, formatted to one decimal place with an `mA` unit label. The widget SHALL include a status dot that follows the same online/offline and pending-reading pattern as sensor widgets on the Sensors dashboard.

#### Scenario: Current widget updates on new reading

- **WHEN** the page receives a WebSocket `current` event with `"ma": 12.3`
- **THEN** the current widget displays `12.3` with unit `mA`

#### Scenario: Current widget seeds from status API

- **WHEN** a user loads `/digital` and `GET /api/status` returns `"last_current_ma": 5.7`
- **THEN** the current widget displays `5.7` before any new serial data arrives

### Requirement: Current mA history graph

The Digital Signal dashboard SHALL include a current history graph that plots current in milliamps over time as a line chart with a rolling client-side history buffer. The Y-axis SHALL range from `0` to `500` mA.

#### Scenario: History graph updates on new current reading

- **WHEN** the page receives a WebSocket `current` event with `"ma": 12.3`
- **THEN** the current history graph appends a point at Y=`12.3`

#### Scenario: History graph Y-axis range

- **WHEN** the current history graph is rendered
- **THEN** the Y-axis displays values from `0` to `500` mA

### Requirement: WebSocket cached current value on connect

When a WebSocket client connects, the server SHALL send the last known current value if available, with `"cached": true`, using the same pattern as potentiometer and detected readings.

#### Scenario: New client receives cached current value

- **WHEN** a WebSocket client connects and a current reading has previously been parsed
- **THEN** the server sends `{"type": "current", "ma": <float>, "cached": true}` before any new serial data arrives
