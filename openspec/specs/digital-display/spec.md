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

`GET /api/status` SHALL include `last_logic_value` as an integer `0`, `1`, or `null` when no reading has been received. It SHALL also include `last_potentiometer_v` as a float or `null`, `last_detected_value` as `0`, `1`, or `null` when no reading has been received, and `last_current_ma` as a float or `null` when no current reading has been received. The pot undefined zone (1.5–3.0 V) SHALL be reported as detected value `0`.

#### Scenario: Status includes last logic value

- **WHEN** a client requests `GET /api/status` after a SIGNAL_PIN logic line has been parsed
- **THEN** the response includes `"last_logic_value": 0` or `"last_logic_value": 1`

#### Scenario: Status includes last potentiometer voltage

- **WHEN** a client requests `GET /api/status` after a `Pot:` line has been parsed
- **THEN** the response includes `"last_potentiometer_v"` as a float (e.g. `2.5`)

#### Scenario: Status includes last detected value

- **WHEN** a client requests `GET /api/status` after a `Pot:` line with logic data has been parsed
- **THEN** the response includes `"last_detected_value": 0` or `"last_detected_value": 1`

#### Scenario: Status includes last current value

- **WHEN** a client requests `GET /api/status` after a `Pot:` line with a `Current:` field has been parsed
- **THEN** the response includes `"last_current_ma"` as a float (e.g. `12.3`)

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

### Requirement: Detected logic serial ingestion

The system SHALL read the pot-derived logic state from `arduino/simple01.ino` `Pot:` serial lines at 9600 baud. The `Logic:` field SHALL be mapped to detected values `0` or `1` where `Logic: UNDEFINED` (pot voltage in the 1.5–3.0 V zone) maps to `0`. Each parsed line SHALL broadcast to all connected WebSocket clients as JSON `{"type": "detected", "value": <0|1>}`. The detected value reflects the logic zone driving the LED on D9.

#### Scenario: Detected HIGH line received

- **WHEN** the Arduino sends `Pot: 4.00 V | Logic: 1 | PWM: 200\n` over serial
- **THEN** the server broadcasts `{"type": "detected", "value": 1}` to all connected WebSocket clients

#### Scenario: Detected LOW line received

- **WHEN** the Arduino sends `Pot: 1.20 V | Logic: 0\n` over serial
- **THEN** the server broadcasts `{"type": "detected", "value": 0}` to all connected WebSocket clients

#### Scenario: Detected undefined line received

- **WHEN** the Arduino sends `Pot: 2.10 V | Logic: UNDEFINED\n` over serial
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

The Digital Signal dashboard SHALL include a detected logic LED widget that displays the live detected logic state as `0` or `1`, representing the pot-derived logic zone driving the LED on D9. The undefined zone (1.5–3.0 V) SHALL display as `0`. The widget SHALL include a status dot that follows the same online/offline and pending-reading pattern as sensor widgets on the Sensors dashboard.

#### Scenario: Detected widget updates on new reading

- **WHEN** the page receives a WebSocket `detected` event with `"value": 1`
- **THEN** the detected logic LED widget displays `1`

#### Scenario: Detected widget updates on undefined reading

- **WHEN** the page receives a WebSocket `detected` event with `"value": 0` from a pot line in the undefined zone
- **THEN** the detected logic LED widget displays `0`

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

### Requirement: Detected logic LED history graph

The Digital Signal dashboard SHALL include a detected logic LED history graph that plots detected state over time as a stepped line chart with Y-axis values `0` and `1`. The undefined pot zone (1.5–3.0 V) SHALL be plotted as `0`.

#### Scenario: History graph updates on undefined state

- **WHEN** the page receives a WebSocket `detected` event with `"value": 0` from the undefined zone
- **THEN** the detected logic LED history graph appends a point at Y=`0`

#### Scenario: History graph Y-axis shows two states

- **WHEN** the detected logic LED history graph is rendered
- **THEN** the Y-axis displays ticks at `0` and `1`

### Requirement: Potentiometer history graph

The Digital Signal dashboard SHALL include a potentiometer history graph titled **Potentiometer history, V** that plots voltage over time with a rolling client-side history buffer. The Y-axis SHALL be labeled **V** and range from `0` to `5` V.

#### Scenario: Potentiometer history Y-axis labeled in volts

- **WHEN** the potentiometer history graph is rendered
- **THEN** the Y-axis displays the unit label `V`

### Requirement: Potentiometer graph logic zone boundaries

The potentiometer history graph SHALL display horizontal dashed reference lines at **1.5 V** (green) and **3.0 V** (red), matching the logic zone thresholds in `arduino/simple01.ino`.

#### Scenario: Low zone boundary visible

- **WHEN** the potentiometer history graph is rendered
- **THEN** a green dashed line is displayed at Y=`1.5` V

#### Scenario: High zone boundary visible

- **WHEN** the potentiometer history graph is rendered
- **THEN** a red dashed line is displayed at Y=`3.0` V

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

### Requirement: Shunt resistor history graph

The Digital Signal dashboard SHALL include a shunt resistor history graph titled **Shunt resistor history, mA** that plots current in milliamps over time as a line chart with a rolling client-side history buffer. The Y-axis SHALL be labeled **mA** and range from `0` to `500` mA. The graph SHALL appear immediately after the potentiometer history graph on the dashboard.

#### Scenario: History graph updates on new current reading

- **WHEN** the page receives a WebSocket `current` event with `"ma": 12.3`
- **THEN** the shunt resistor history graph appends a point at Y=`12.3`

#### Scenario: History graph Y-axis labeled in milliamps

- **WHEN** the shunt resistor history graph is rendered
- **THEN** the Y-axis displays the unit label `mA` and values from `0` to `500`

### Requirement: WebSocket cached current value on connect

When a WebSocket client connects, the server SHALL send the last known current value if available, with `"cached": true`, using the same pattern as potentiometer and detected readings.

#### Scenario: New client receives cached current value

- **WHEN** a WebSocket client connects and a current reading has previously been parsed
- **THEN** the server sends `{"type": "current", "ma": <float>, "cached": true}` before any new serial data arrives
