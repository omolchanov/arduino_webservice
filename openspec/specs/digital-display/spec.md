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

`GET /api/status` SHALL include `last_logic_value` as an integer `0`, `1`, or `null` when no reading has been received.

#### Scenario: Status includes last logic value

- **WHEN** a client requests `GET /api/status` after a logic line has been parsed
- **THEN** the response includes `"last_logic_value": 0` or `"last_logic_value": 1`

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
