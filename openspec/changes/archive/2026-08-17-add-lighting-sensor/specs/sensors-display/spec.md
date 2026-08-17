## ADDED Requirements

### Requirement: Sensor read interval in Arduino sketches

Each sensor Arduino sketch SHALL sample its sensor and publish a serial line at most once per second. The read/publish cadence SHALL be enforced in firmware (e.g. `delay(1000)` at the end of `loop()`), not in the Python server or browser.

#### Scenario: Light sketch publishes every second

- **WHEN** `arduino/light.ino` is running on the Arduino
- **THEN** the sketch sends at most one `Light: <integer>` line per second

#### Scenario: Distance sketch publishes every second

- **WHEN** `arduino/distance.ino` is running on the Arduino
- **THEN** the sketch sends at most one `Distance: <number> cm` line per second

### Requirement: LDR light level serial ingestion

The system SHALL read light level measurements from an Arduino Uno over USB serial at 9600 baud. Lines in the format `Light: <integer>` SHALL be parsed and broadcast to all connected WebSocket clients as JSON `{"type": "light", "level": <integer>}`. The integer SHALL be the inverted ADC value as sent by the Arduino (0–1023, higher = brighter).

#### Scenario: Light line received

- **WHEN** the Arduino sends `Light: 512\n` over serial
- **THEN** the server broadcasts `{"type": "light", "level": 512}` to all connected WebSocket clients

#### Scenario: Invalid light line ignored

- **WHEN** the serial port sends a line that does not match the light format
- **THEN** the server does not broadcast a light event (may still parse as distance or keypad if applicable)

## MODIFIED Requirements

### Requirement: Sensors page

The system SHALL serve a web page at `GET /sensors` that displays live sensor readings from the Arduino. The page SHALL include a **Distance** section showing the latest value in centimeters and a **Lighting level** section showing the latest inverted ADC integer. A sidebar SHALL provide navigation to Keypad and Sensors. Connection status SHALL be shown as a single **Online** / **Offline** label in the top-right corner of the page (not as a per-page widget).

#### Scenario: Distance updates on Sensors page

- **WHEN** a WebSocket client on `/sensors` receives a distance broadcast
- **THEN** the Distance section updates to show the new value in cm

#### Scenario: Lighting level updates on Sensors page

- **WHEN** a WebSocket client on `/sensors` receives a light broadcast
- **THEN** the Lighting level section updates to show the new integer value

#### Scenario: Navigation between pages

- **WHEN** a user opens `/` or `/sensors`
- **THEN** both pages show sidebar navigation links to switch between Keypad and Sensors
