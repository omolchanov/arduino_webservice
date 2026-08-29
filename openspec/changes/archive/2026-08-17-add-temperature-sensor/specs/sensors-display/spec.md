## ADDED Requirements

### Requirement: LM35 temperature serial ingestion

The system SHALL read temperature measurements from an Arduino Uno over USB serial at 9600 baud. Lines in the format `Temperature: <number> C` SHALL be parsed and broadcast to all connected WebSocket clients as JSON `{"type": "temperature", "c": <number>}`. The value SHALL be degrees Celsius as computed by the Arduino firmware (LM35: 10 mV/°C).

#### Scenario: Temperature line received

- **WHEN** the Arduino sends `Temperature: 23.45 C\n` over serial
- **THEN** the server broadcasts `{"type": "temperature", "c": 23.45}` to all connected WebSocket clients

#### Scenario: Invalid temperature line ignored

- **WHEN** the serial port sends a line that does not match the temperature format
- **THEN** the server does not broadcast a temperature event (may still parse as distance, light, or keypad if applicable)

## MODIFIED Requirements

### Requirement: Sensor read interval in Arduino firmware

The combined sensor sketch (`arduino/sensors/sensors.ino`) SHALL sample all sensors and publish serial lines at most once every five seconds. The read/publish cadence SHALL be enforced in firmware (`delay(5000)` at the end of `loop()`), not in the Python server or browser.

#### Scenario: Combined sensors sketch publishes every five seconds

- **WHEN** `arduino/sensors/sensors.ino` is running on the Arduino
- **THEN** the sketch sends at most one `Distance: <number> cm` line, one `Light: <integer>` line, and one `Temperature: <number> C` line per five-second cycle

### Requirement: Sensors page

The system SHALL serve a web page at `GET /sensors` that displays live sensor readings from the Arduino. The page SHALL include a **Distance** section showing the latest value in centimeters, a **Lighting level** section showing the latest inverted ADC integer with a **units** label, and a **Temperature** section showing the latest value in degrees Celsius with a **°C** label. Each sensor card header SHALL display a small status dot immediately to the right of the sensor name. A sidebar SHALL provide navigation to Keypad and Sensors. Connection status SHALL be shown as a single **Online** / **Offline** label in the top-right corner of the page (not as a per-page widget).

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

### Requirement: Per-sensor status dot on Sensors page

Each sensor card on `/sensors` (**Distance**, **Lighting level**, **Temperature**) SHALL show a small circular status dot to the right of the card header name. The dot SHALL use three visual states: **grey** (initializing), **green** (valid data), and **red** (invalid data or Arduino offline). State SHALL be determined in the browser from live WebSocket `distance`/`light`/`temperature` events; cached WebSocket snapshots SHALL update displayed values only and SHALL NOT affect dot state.

A reading is **valid** when distance `cm > 0`, light `level > 0`, or temperature `c` is a finite number within **-55 to 150 °C** (LM35 range). Distance and light readings of **0** are **invalid**. While in the initializing state, the first live reading SHALL immediately set the dot to green (valid) or red (invalid). Transitions between green and red after initialization SHALL be debounced by 10 seconds — the dot SHALL change only after readings remain consistently valid or invalid for 10 seconds.

#### Scenario: Dots start grey on page load

- **WHEN** a user opens `/sensors` before live sensor data is evaluated
- **THEN** all sensor status dots are grey

#### Scenario: Dot resolves immediately from initializing

- **WHEN** Arduino is online and the page receives the first live reading for a sensor
- **THEN** that sensor's dot immediately turns green if the value is valid, or red if invalid

#### Scenario: Dot debounces green to red

- **WHEN** a sensor dot is green and live readings become invalid
- **THEN** the dot stays green for 10 seconds and turns red only if readings remain invalid

#### Scenario: Dot debounces red to green

- **WHEN** a sensor dot is red and live readings become valid
- **THEN** the dot stays red for 10 seconds and turns green only if readings remain valid

#### Scenario: Dot turns red when no live data while initializing

- **WHEN** Arduino is online but a sensor receives no live reading within 10 seconds of coming online
- **THEN** that sensor's status dot turns red

#### Scenario: All dots red when Arduino is offline

- **WHEN** Arduino serial is disconnected (`serial_connected` is false)
- **THEN** all sensor status dots turn red immediately
