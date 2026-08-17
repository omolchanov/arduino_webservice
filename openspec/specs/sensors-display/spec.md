# sensors-display Specification

## Purpose

Read HC-SR04 ultrasonic distance and LDR light level measurements from an Arduino Uno over USB serial and display live readings in a browser via WebSocket on a dedicated Sensors page.

## Requirements

### Requirement: Sensor read interval in Arduino firmware

The combined sensor sketch (`arduino/sensors/sensors.ino`) SHALL sample all sensors and publish serial lines at most once every five seconds. The read/publish cadence SHALL be enforced in firmware (`delay(5000)` at the end of `loop()`), not in the Python server or browser.

#### Scenario: Combined sensors sketch publishes every five seconds

- **WHEN** `arduino/sensors/sensors.ino` is running on the Arduino
- **THEN** the sketch sends at most one `Distance: <number> cm` line and one `Light: <integer>` line per five-second cycle

### Requirement: Ultrasonic distance serial ingestion

The system SHALL read distance measurements from an Arduino Uno over USB serial at 9600 baud. Lines in the format `Distance: <number> cm` SHALL be parsed and broadcast to all connected WebSocket clients as JSON `{"type": "distance", "cm": <number>}`.

#### Scenario: Distance line received

- **WHEN** the Arduino sends `Distance: 42.50 cm\n` over serial
- **THEN** the server broadcasts `{"type": "distance", "cm": 42.5}` to all connected WebSocket clients

#### Scenario: Invalid distance line ignored

- **WHEN** the serial port sends a line that does not match the distance format
- **THEN** the server does not broadcast a distance event (may still parse as keypad or light if applicable)

### Requirement: LDR light level serial ingestion

The system SHALL read light level measurements from an Arduino Uno over USB serial at 9600 baud. Lines in the format `Light: <integer>` SHALL be parsed and broadcast to all connected WebSocket clients as JSON `{"type": "light", "level": <integer>}`. The integer SHALL be the inverted ADC value as sent by the Arduino (0–1023, higher = brighter).

#### Scenario: Light line received

- **WHEN** the Arduino sends `Light: 512\n` over serial
- **THEN** the server broadcasts `{"type": "light", "level": 512}` to all connected WebSocket clients

#### Scenario: Invalid light line ignored

- **WHEN** the serial port sends a line that does not match the light format
- **THEN** the server does not broadcast a light event (may still parse as distance or keypad if applicable)

### Requirement: Sensors page

The system SHALL serve a web page at `GET /sensors` that displays live sensor readings from the Arduino. The page SHALL include a **Distance** section showing the latest value in centimeters and a **Lighting level** section showing the latest inverted ADC integer with a **units** label. Each sensor card header SHALL display a small status dot immediately to the right of the sensor name. A sidebar SHALL provide navigation to Keypad and Sensors. Connection status SHALL be shown as a single **Online** / **Offline** label in the top-right corner of the page (not as a per-page widget).

#### Scenario: Distance updates on Sensors page

- **WHEN** a WebSocket client on `/sensors` receives a distance broadcast
- **THEN** the Distance section updates to show the new value in cm

#### Scenario: Lighting level updates on Sensors page

- **WHEN** a WebSocket client on `/sensors` receives a light broadcast
- **THEN** the Lighting level section updates to show the new integer value

#### Scenario: Navigation between pages

- **WHEN** a user opens `/` or `/sensors`
- **THEN** both pages show sidebar navigation links to switch between Keypad and Sensors

### Requirement: Per-sensor status dot on Sensors page

Each sensor card on `/sensors` (**Distance**, **Lighting level**) SHALL show a small circular status dot to the right of the card header name. The dot SHALL use three visual states: **grey** (initializing), **green** (valid data), and **red** (invalid data or Arduino offline). State SHALL be determined in the browser from live WebSocket `distance`/`light` events; cached WebSocket snapshots SHALL update displayed values only and SHALL NOT affect dot state.

A reading is **valid** when distance `cm > 0` or light `level > 0`; a reading of **0** is **invalid**. While in the initializing state, the first live reading SHALL immediately set the dot to green (valid) or red (invalid). Transitions between green and red after initialization SHALL be debounced by 10 seconds — the dot SHALL change only after readings remain consistently valid or invalid for 10 seconds.

#### Scenario: Dots start grey on page load

- **WHEN** a user opens `/sensors` before live sensor data is evaluated
- **THEN** both sensor status dots are grey

#### Scenario: Dot resolves immediately from initializing

- **WHEN** Arduino is online and the page receives the first live reading for a sensor
- **THEN** that sensor's dot immediately turns green if the value is valid, or red if the value is 0

#### Scenario: Dot debounces green to red

- **WHEN** a sensor dot is green and live readings become invalid (value 0)
- **THEN** the dot stays green for 10 seconds and turns red only if readings remain invalid

#### Scenario: Dot debounces red to green

- **WHEN** a sensor dot is red and live readings become valid (value > 0)
- **THEN** the dot stays red for 10 seconds and turns green only if readings remain valid

#### Scenario: Dot turns red when no live data while initializing

- **WHEN** Arduino is online but a sensor receives no live reading within 10 seconds of coming online
- **THEN** that sensor's status dot turns red

#### Scenario: All dots red when Arduino is offline

- **WHEN** Arduino serial is disconnected (`serial_connected` is false)
- **THEN** all sensor status dots turn red immediately
