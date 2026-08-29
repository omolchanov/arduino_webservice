# sensors-display Specification

## Purpose

Read HC-SR04 ultrasonic distance, LDR light level, and LM35 temperature measurements from an Arduino Uno over USB serial and display live readings in a browser via WebSocket on a dedicated Sensors page.

## Requirements

### Requirement: Sensor read interval in Arduino firmware

The combined sensor sketch (`arduino/sensors/sensors.ino`) SHALL sample all sensors and publish serial lines at most once per second. The read/publish cadence SHALL be enforced in firmware (`delay(1000)` at the end of `loop()`), not in the Python server or browser.

#### Scenario: Combined sensors sketch publishes every second

- **WHEN** `arduino/sensors/sensors.ino` is running on the Arduino
- **THEN** the sketch sends at most one `Distance: <number> cm` line, one `Light: <integer>` line, and one `Temperature: <number> C` line per one-second cycle

### Requirement: Ultrasonic distance serial ingestion

The system SHALL read distance measurements from an Arduino Uno over USB serial at 9600 baud. Lines in the format `Distance: <number> cm` SHALL be parsed and broadcast to all connected WebSocket clients as JSON `{"type": "distance", "cm": <number>}`.

#### Scenario: Distance line received

- **WHEN** the Arduino sends `Distance: 42.50 cm\n` over serial
- **THEN** the server broadcasts `{"type": "distance", "cm": 42.5}` to all connected WebSocket clients

#### Scenario: Invalid distance line ignored

- **WHEN** the serial port sends a line that does not match the distance format
- **THEN** the server does not broadcast a distance event (may still parse as light, temperature, or keypad if applicable)

### Requirement: LDR light level serial ingestion

The system SHALL read light level measurements from an Arduino Uno over USB serial at 9600 baud. Lines in the format `Light: <integer>` SHALL be parsed and broadcast to all connected WebSocket clients as JSON `{"type": "light", "level": <integer>}`. The integer SHALL be the inverted ADC value as sent by the Arduino (0–1023, higher = brighter).

#### Scenario: Light line received

- **WHEN** the Arduino sends `Light: 512\n` over serial
- **THEN** the server broadcasts `{"type": "light", "level": 512}` to all connected WebSocket clients

#### Scenario: Invalid light line ignored

- **WHEN** the serial port sends a line that does not match the light format
- **THEN** the server does not broadcast a light event (may still parse as distance, temperature, or keypad if applicable)

### Requirement: LM35 temperature serial ingestion

The system SHALL read temperature measurements from an Arduino Uno over USB serial at 9600 baud. Lines in the format `Temperature: <number> C` SHALL be parsed and broadcast to all connected WebSocket clients as JSON `{"type": "temperature", "c": <number>}`. The value SHALL be degrees Celsius as computed by the Arduino firmware.

#### Scenario: Temperature line received

- **WHEN** the Arduino sends `Temperature: 23.45 C\n` over serial
- **THEN** the server broadcasts `{"type": "temperature", "c": 23.45}` to all connected WebSocket clients

#### Scenario: Invalid temperature line ignored

- **WHEN** the serial port sends a line that does not match the temperature format
- **THEN** the server does not broadcast a temperature event (may still parse as distance, light, or keypad if applicable)

### Requirement: Sensors page

The system SHALL serve a web page at `GET /sensors` that displays live sensor readings from the Arduino. The page SHALL include a **Distance** section showing the latest value in centimeters, a **Lighting level** section showing the latest inverted ADC integer with a **units** label, and a **Temperature** section showing the latest value in degrees Celsius with a **°C** label. A sidebar SHALL provide navigation to Keypad and Sensors. Connection status SHALL be shown as a single **Online** / **Offline** label in the top-right corner of the page.

#### Scenario: Distance updates on Sensors page

- **WHEN** a WebSocket client on `/sensors` receives a distance broadcast
- **THEN** the Distance section updates to show the new value in cm

#### Scenario: Lighting level updates on Sensors page

- **WHEN** a WebSocket client on `/sensors` receives a light broadcast
- **THEN** the Lighting level section updates to show the new integer value

#### Scenario: Temperature updates on Sensors page

- **WHEN** a WebSocket client on `/sensors` receives a temperature broadcast
- **THEN** the Temperature section updates to show the new value in °C (one decimal place)

#### Scenario: Navigation between pages

- **WHEN** a user opens `/` or `/sensors`
- **THEN** both pages show sidebar navigation links to switch between Keypad and Sensors
