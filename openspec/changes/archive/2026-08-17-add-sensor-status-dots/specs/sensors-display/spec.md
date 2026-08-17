## MODIFIED Requirements

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

Each sensor card on `/sensors` (**Distance**, **Lighting level**) SHALL show a small circular status dot to the right of the card header name. The dot SHALL use three visual states: **grey** (initializing), **green** (data received), and **red** (no data or Arduino offline). State SHALL be determined in the browser using existing WebSocket messages and `/api/status` responses; no new server endpoints are required.

#### Scenario: Dots start grey on page load

- **WHEN** a user opens `/sensors` and Arduino connection status is not yet known
- **THEN** both sensor status dots are grey

#### Scenario: Dot turns green when sensor data arrives

- **WHEN** Arduino is online and the page receives a valid reading for a sensor (WebSocket `distance`/`light` event or non-null value from `/api/status`)
- **THEN** that sensor's status dot turns green

#### Scenario: Dot turns red when sensor receives no data

- **WHEN** Arduino is online but a sensor has not received any valid reading within 10 seconds of Arduino coming online
- **THEN** that sensor's status dot turns red

#### Scenario: All dots red when Arduino is offline

- **WHEN** Arduino serial is disconnected (`serial_connected` is false)
- **THEN** all sensor status dots are red
