## MODIFIED Requirements

### Requirement: Logic value in status API

`GET /api/status` SHALL include `last_logic_value` as an integer `0`, `1`, or `null` when no reading has been received. It SHALL also include `last_potentiometer_v` as a float or `null`, `last_detected_value` as `0`, `1`, or `null` when no reading has been received, `last_current_ma` as a float or `null` when no current reading has been received, and `last_led_resistance_ohm` as a float or `null` when no resistance reading has been received. The pot undefined zone (1.5–3.0 V) SHALL be reported as detected value `0`.

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

#### Scenario: Status includes last resistance value

- **WHEN** a client requests `GET /api/status` after a `Pot:` line with a `LED Resistance:` field has been parsed
- **THEN** the response includes `"last_led_resistance_ohm"` as a float (e.g. `162.6`)

### Requirement: Potentiometer serial ingestion

The system SHALL read potentiometer voltage from `arduino/simple01.ino` serial lines at 9600 baud. Lines matching `Pot: <voltage> V | Logic: <state>` with optional `| PWM: <n>`, `| Shunt: <voltage> V`, `| Current: <mA> mA`, and `| LED Resistance: <ohm> Ohm` suffixes SHALL be parsed and the voltage field SHALL be broadcast to all connected WebSocket clients as JSON `{"type": "potentiometer", "v": <float>}`. Lines without the shunt/current/resistance suffixes SHALL remain valid.

#### Scenario: Potentiometer line received

- **WHEN** the Arduino sends `Pot: 2.50 V | Logic: 0\n` over serial
- **THEN** the server broadcasts `{"type": "potentiometer", "v": 2.5}` to all connected WebSocket clients

#### Scenario: Potentiometer line with PWM suffix received

- **WHEN** the Arduino sends `Pot: 4.00 V | Logic: 1 | PWM: 200\n` over serial
- **THEN** the server broadcasts `{"type": "potentiometer", "v": 4.0}` to all connected WebSocket clients

#### Scenario: Potentiometer line with current suffix received

- **WHEN** the Arduino sends `Pot: 4.00 V | Logic: 1 | PWM: 200 | Shunt: 0.123 V | Current: 12.3 mA\n` over serial
- **THEN** the server broadcasts `{"type": "potentiometer", "v": 4.0}` to all connected WebSocket clients

#### Scenario: Potentiometer line with resistance suffix received

- **WHEN** the Arduino sends `Pot: 4.00 V | Logic: 1 | Shunt: 0.123 V | Current: 12.3 mA | LED Resistance: 162.6 Ohm\n` over serial
- **THEN** the server broadcasts `{"type": "potentiometer", "v": 4.0}` to all connected WebSocket clients

#### Scenario: Invalid potentiometer line ignored

- **WHEN** the serial port sends a line that does not match the `Pot:` format
- **THEN** the server does not broadcast a potentiometer event

## ADDED Requirements

### Requirement: Resistance serial ingestion

The system SHALL read the LED resistance measurement from `arduino/simple01.ino` `Pot:` serial lines at 9600 baud when the line includes a `LED Resistance: <ohm> Ohm` field. Each parsed line SHALL broadcast to all connected WebSocket clients as JSON `{"type": "resistance", "ohm": <float>}`.

#### Scenario: Resistance line received

- **WHEN** the Arduino sends `Pot: 4.00 V | Logic: 1 | Shunt: 0.123 V | Current: 12.3 mA | LED Resistance: 162.6 Ohm\n` over serial
- **THEN** the server broadcasts `{"type": "resistance", "ohm": 162.6}` to all connected WebSocket clients

#### Scenario: Line without resistance field does not broadcast resistance

- **WHEN** the Arduino sends `Pot: 2.50 V | Logic: 0\n` over serial
- **THEN** the server does not broadcast a resistance event

### Requirement: Resistance widget

The Digital Signal dashboard SHALL include a resistance widget that displays the live LED resistance reading formatted to one decimal place with a **Ω** unit label. The widget SHALL include a status dot that follows the same online/offline and pending-reading pattern as sensor widgets on the Sensors dashboard.

#### Scenario: Resistance widget updates on new reading

- **WHEN** the page receives a WebSocket `resistance` event with `"ohm": 162.6`
- **THEN** the resistance widget displays `162.6` with unit `Ω`

#### Scenario: Resistance widget seeds from status API

- **WHEN** a user loads `/digital` and `GET /api/status` returns `"last_led_resistance_ohm": 85.3`
- **THEN** the resistance widget displays `85.3` before any new serial data arrives

### Requirement: Resistance history graph

The Digital Signal dashboard SHALL include a resistance history graph titled **Resistance history, Ω** that plots LED resistance over time as a line chart with a rolling client-side history buffer. The Y-axis SHALL be labeled **Ω** and range from `0` to `2000` Ω. The graph SHALL appear immediately after the shunt resistor history (mA) graph on the dashboard.

#### Scenario: History graph updates on new resistance reading

- **WHEN** the page receives a WebSocket `resistance` event with `"ohm": 162.6`
- **THEN** the resistance history graph appends a point at Y=`162.6`

#### Scenario: History graph Y-axis labeled in ohms

- **WHEN** the resistance history graph is rendered
- **THEN** the Y-axis displays the unit label `Ω` and values from `0` to `2000`

#### Scenario: History graph placement after mA history

- **WHEN** the Digital Signal dashboard is rendered
- **THEN** the resistance history graph appears directly after the shunt resistor history (mA) graph

### Requirement: WebSocket cached resistance value on connect

When a WebSocket client connects, the server SHALL send the last known resistance value if available, with `"cached": true`, using the same pattern as current and potentiometer readings.

#### Scenario: New client receives cached resistance value

- **WHEN** a WebSocket client connects and a resistance reading has previously been parsed
- **THEN** the server sends `{"type": "resistance", "ohm": <float>, "cached": true}` before any new serial data arrives
