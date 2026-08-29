## MODIFIED Requirements

### Requirement: Logic signal serial ingestion

The system SHALL read digital logic measurements from an Arduino Uno over USB serial at 9600 baud. Lines from `arduino/simple01.ino` matching `SIGNAL_PIN: Logic 0 (LOW)` or `SIGNAL_PIN: Logic 1 (HIGH)` SHALL be parsed and broadcast to all connected WebSocket clients as JSON `{"type": "logic", "value": <0|1>}`. Only the SIGNAL_PIN phase value is required for the logic signal graph widget.

#### Scenario: Logic HIGH line received

- **WHEN** the Arduino sends `SIGNAL_PIN: Logic 1 (HIGH)\n` over serial
- **THEN** the server broadcasts `{"type": "logic", "value": 1}` to all connected WebSocket clients

#### Scenario: Logic LOW line received

- **WHEN** the Arduino sends `SIGNAL_PIN: Logic 0 (LOW)\n` over serial
- **THEN** the server broadcasts `{"type": "logic", "value": 0}` to all connected WebSocket clients

#### Scenario: Invalid logic line ignored

- **WHEN** the serial port sends a line that does not match the SIGNAL_PIN logic format
- **THEN** the server does not broadcast a logic event (may still parse as pot, distance, light, or keypad if applicable)

### Requirement: Logic value in status API

`GET /api/status` SHALL include `last_logic_value` as an integer `0`, `1`, or `null` when no reading has been received. It SHALL also include `last_potentiometer_v` as a float or `null` and `last_detected_value` as `0`, `0.5`, `1`, or `null` when no reading has been received. The value `0.5` represents the undefined pot logic zone.

#### Scenario: Status includes last logic value

- **WHEN** a client requests `GET /api/status` after a SIGNAL_PIN logic line has been parsed
- **THEN** the response includes `"last_logic_value": 0` or `"last_logic_value": 1`

#### Scenario: Status includes last potentiometer voltage

- **WHEN** a client requests `GET /api/status` after a `Pot:` line has been parsed
- **THEN** the response includes `"last_potentiometer_v"` as a float (e.g. `2.5`)

#### Scenario: Status includes last detected value

- **WHEN** a client requests `GET /api/status` after a `Pot:` line with logic data has been parsed
- **THEN** the response includes `"last_detected_value": 0`, `"last_detected_value": 0.5`, or `"last_detected_value": 1`

### Requirement: Potentiometer serial ingestion

The system SHALL read potentiometer voltage from `arduino/simple01.ino` serial lines at 9600 baud. Lines matching `Pot: <voltage> V | Logic: <state>` (with optional `| PWM: <n>` suffix) SHALL be parsed and the voltage field SHALL be broadcast to all connected WebSocket clients as JSON `{"type": "potentiometer", "v": <float>}`.

#### Scenario: Potentiometer line received

- **WHEN** the Arduino sends `Pot: 2.50 V | Logic: 0\n` over serial
- **THEN** the server broadcasts `{"type": "potentiometer", "v": 2.5}` to all connected WebSocket clients

#### Scenario: Potentiometer line with PWM suffix received

- **WHEN** the Arduino sends `Pot: 4.00 V | Logic: 1 | PWM: 200\n` over serial
- **THEN** the server broadcasts `{"type": "potentiometer", "v": 4.0}` to all connected WebSocket clients

#### Scenario: Invalid potentiometer line ignored

- **WHEN** the serial port sends a line that does not match the `Pot:` format
- **THEN** the server does not broadcast a potentiometer event

### Requirement: Detected logic serial ingestion

The system SHALL read the pot-derived logic state from `arduino/simple01.ino` `Pot:` serial lines at 9600 baud. The `Logic:` field SHALL be mapped to detected values `0`, `0.5`, or `1` where `Logic: UNDEFINED` maps to `0.5`. Each parsed line SHALL broadcast to all connected WebSocket clients as JSON `{"type": "detected", "value": <0|0.5|1>}`. The detected value reflects the logic zone driving the LED on D9.

#### Scenario: Detected HIGH line received

- **WHEN** the Arduino sends `Pot: 4.00 V | Logic: 1 | PWM: 200\n` over serial
- **THEN** the server broadcasts `{"type": "detected", "value": 1}` to all connected WebSocket clients

#### Scenario: Detected LOW line received

- **WHEN** the Arduino sends `Pot: 1.20 V | Logic: 0\n` over serial
- **THEN** the server broadcasts `{"type": "detected", "value": 0}` to all connected WebSocket clients

#### Scenario: Detected undefined line received

- **WHEN** the Arduino sends `Pot: 2.10 V | Logic: UNDEFINED\n` over serial
- **THEN** the server broadcasts `{"type": "detected", "value": 0.5}` to all connected WebSocket clients

### Requirement: Detected logic LED widget

The Digital Signal dashboard SHALL include a detected logic LED widget that displays the live detected logic state as `0`, `0.5`, or `1`, representing the pot-derived logic zone driving the LED on D9. The value `0.5` represents the undefined zone. The widget SHALL include a status dot that follows the same online/offline and pending-reading pattern as sensor widgets on the Sensors dashboard.

#### Scenario: Detected widget updates on new reading

- **WHEN** the page receives a WebSocket `detected` event with `"value": 1`
- **THEN** the detected logic LED widget displays `1`

#### Scenario: Detected widget updates on undefined reading

- **WHEN** the page receives a WebSocket `detected` event with `"value": 0.5`
- **THEN** the detected logic LED widget displays `0.5`

#### Scenario: Detected widget seeds from status API

- **WHEN** a user loads `/digital` and `GET /api/status` returns `"last_detected_value": 0.5`
- **THEN** the detected logic LED widget displays `0.5` before any new serial data arrives

### Requirement: WebSocket cached potentiometer and detected values on connect

When a WebSocket client connects, the server SHALL send the last known potentiometer voltage and detected logic value if available, each with `"cached": true`, using the same pattern as logic, distance, and light readings.

#### Scenario: New client receives cached potentiometer value

- **WHEN** a WebSocket client connects and a potentiometer reading has previously been parsed
- **THEN** the server sends `{"type": "potentiometer", "v": <float>, "cached": true}` before any new serial data arrives

#### Scenario: New client receives cached detected value

- **WHEN** a WebSocket client connects and a detected logic value has previously been parsed
- **THEN** the server sends `{"type": "detected", "value": <0|0.5|1>, "cached": true}` before any new serial data arrives

## ADDED Requirements

### Requirement: Detected logic LED history graph

The Digital Signal dashboard SHALL include a detected logic LED history graph that plots detected state over time as a stepped line chart with Y-axis values `0`, `0.5`, and `1`.

#### Scenario: History graph updates on undefined state

- **WHEN** the page receives a WebSocket `detected` event with `"value": 0.5`
- **THEN** the detected logic LED history graph appends a point at Y=`0.5`

#### Scenario: History graph Y-axis shows three states

- **WHEN** the detected logic LED history graph is rendered
- **THEN** the Y-axis displays ticks at `0`, `0.5`, and `1`

### Requirement: Potentiometer graph logic zone boundaries

The potentiometer history graph SHALL display horizontal dashed reference lines at **1.5 V** (green) and **3.0 V** (red), matching the logic zone thresholds in `arduino/simple01.ino`.

#### Scenario: Low zone boundary visible

- **WHEN** the potentiometer history graph is rendered
- **THEN** a green dashed line is displayed at Y=`1.5` V

#### Scenario: High zone boundary visible

- **WHEN** the potentiometer history graph is rendered
- **THEN** a red dashed line is displayed at Y=`3.0` V
