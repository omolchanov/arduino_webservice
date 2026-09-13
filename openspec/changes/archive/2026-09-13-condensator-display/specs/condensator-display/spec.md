## Purpose

Read capacitor voltage and charge measurements from `arduino/condensator/condensator.ino` over USB serial and display live values with rolling history graphs on a dedicated Condensator page in the browser via WebSocket.

## ADDED Requirements

### Requirement: Condensator phase serial ingestion

The system SHALL read condensator phase markers from an Arduino Uno over USB serial at 9600 baud. Lines exactly matching `Charging...` or `Discharging...` SHALL update the current phase and broadcast to all connected WebSocket clients as JSON `{"type": "condensator_phase", "phase": "charging"}` or `{"type": "condensator_phase", "phase": "discharging"}` respectively.

#### Scenario: Charging phase marker received

- **WHEN** the Arduino sends `Charging...\n` over serial
- **THEN** the server broadcasts `{"type": "condensator_phase", "phase": "charging"}` to all connected WebSocket clients

#### Scenario: Discharging phase marker received

- **WHEN** the Arduino sends `Discharging...\n` over serial
- **THEN** the server broadcasts `{"type": "condensator_phase", "phase": "discharging"}` to all connected WebSocket clients

### Requirement: Condensator voltage and charge serial ingestion

The system SHALL read condensator measurement lines from an Arduino Uno over USB serial at 9600 baud. Lines in the format `V = <number> V   Q = <number> uC` SHALL be parsed and broadcast to all connected WebSocket clients as JSON `{"type": "condensator", "v": <number>, "q_uc": <number>}`. The voltage value SHALL be in volts; the charge value SHALL be in microcoulombs as sent by the Arduino firmware.

#### Scenario: Measurement line received

- **WHEN** the Arduino sends `V = 2.45 V   Q = 539.0 uC\n` over serial
- **THEN** the server broadcasts `{"type": "condensator", "v": 2.45, "q_uc": 539.0}` to all connected WebSocket clients

#### Scenario: Invalid condensator line ignored

- **WHEN** the serial port sends a line that does not match the condensator measurement or phase format
- **THEN** the server does not broadcast a condensator event (may still parse as another message type if applicable)

### Requirement: Condensator page

The system SHALL serve a web page at `GET /condensator` that displays live condensator readings from the Arduino. The page SHALL include a **Voltage** widget showing the latest value in volts (two decimal places) and a **Charge Q** widget showing the latest value in microcoulombs (one decimal place). Each widget SHALL include a rolling time-series graph of recent readings. The voltage graph SHALL show dashed horizontal reference lines at 0 V and 5 V representing RC asymptotes. The charge graph SHALL show dashed horizontal reference lines at 0 µC and 1100 µC (220 µF × 5 V). The page SHALL display the current phase label **Charging** or **Discharging** when phase markers have been received. A sidebar SHALL provide navigation to other dashboard pages including Condensator. Connection status SHALL be shown as **Online** / **Offline** in the top-right corner. Notifications SHALL use custom toasts, not browser alerts.

#### Scenario: Voltage updates on Condensator page

- **WHEN** a WebSocket client on `/condensator` receives a condensator measurement broadcast
- **THEN** the Voltage widget updates to show the new value in V and appends a point to the voltage graph

#### Scenario: Charge Q updates on Condensator page

- **WHEN** a WebSocket client on `/condensator` receives a condensator measurement broadcast
- **THEN** the Charge Q widget updates to show the new value in µC and appends a point to the charge graph

#### Scenario: Phase label updates on Condensator page

- **WHEN** a WebSocket client on `/condensator` receives a condensator_phase broadcast
- **THEN** the page phase label updates to Charging or Discharging accordingly

#### Scenario: Navigation includes Condensator

- **WHEN** a user opens any existing dashboard page
- **THEN** the sidebar includes a link to `/condensator`
