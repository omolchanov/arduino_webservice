# sensors-display Specification

## Purpose

Read HC-SR04 ultrasonic distance measurements from an Arduino Uno over USB serial and display live readings in a browser via WebSocket on a dedicated Sensors page.

## Requirements

### Requirement: Ultrasonic distance serial ingestion

The system SHALL read distance measurements from an Arduino Uno over USB serial at 9600 baud. Lines in the format `Distance: <number> cm` SHALL be parsed and broadcast to all connected WebSocket clients as JSON `{"type": "distance", "cm": <number>}`.

#### Scenario: Distance line received

- **WHEN** the Arduino sends `Distance: 42.50 cm\n` over serial
- **THEN** the server broadcasts `{"type": "distance", "cm": 42.5}` to all connected WebSocket clients

#### Scenario: Invalid distance line ignored

- **WHEN** the serial port sends a line that does not match the distance format
- **THEN** the server does not broadcast a distance event (may still parse as keypad if applicable)

### Requirement: Sensors page

The system SHALL serve a web page at `GET /sensors` that displays live distance readings from the Arduino. The page SHALL include a **Distance** section showing the latest value in centimeters. A sidebar SHALL provide navigation to Keypad and Sensors. Connection status SHALL be shown as a single **Online** / **Offline** label in the top-right corner of the page (not as a per-page widget).

#### Scenario: Distance updates on Sensors page

- **WHEN** a WebSocket client on `/sensors` receives a distance broadcast
- **THEN** the Distance section updates to show the new value in cm

#### Scenario: Navigation between pages

- **WHEN** a user opens `/` or `/sensors`
- **THEN** both pages show sidebar navigation links to switch between Keypad and Sensors
