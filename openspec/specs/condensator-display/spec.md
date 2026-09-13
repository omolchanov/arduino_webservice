# condensator-display Specification

## Purpose

Read capacitor voltage and charge measurements from `arduino/condensator/condensator.ino` over USB serial and display live values with rolling history graphs on a dedicated Condensator page in the browser via WebSocket.

## Requirements

### Requirement: One sketch per Condensator dashboard

The Condensator dashboard SHALL be driven exclusively by the dedicated firmware at `arduino/condensator/condensator.ino`. The system SHALL NOT require or support combining this dashboard with other sketches in a single firmware upload.

#### Scenario: User runs Condensator dashboard

- **WHEN** the user wants to view the Condensator dashboard at `/condensator`
- **THEN** the user uploads `arduino/condensator/condensator.ino` to the Arduino (not `valves.ino`, `mux.ino`, or other production sketches)

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

### Requirement: Condensator values in status API

`GET /api/status` SHALL include `last_condensator_v`, `last_condensator_q_uc`, and `last_condensator_phase` as a float, float, and string (`"charging"` or `"discharging"`) respectively, or `null` when no reading has been received.

#### Scenario: Status includes last condensator values

- **WHEN** a client requests `GET /api/status` after condensator measurement and phase lines have been parsed
- **THEN** the response includes `"last_condensator_v": 2.45`, `"last_condensator_q_uc": 539.0`, and `"last_condensator_phase": "charging"` (or corresponding values from the last readings)

### Requirement: Condensator page

The system SHALL serve a web page at `GET /condensator` that displays live condensator readings from the Arduino. The page SHALL include a **Voltage** widget showing the latest value in volts (two decimal places) and a **Charge Q** widget showing the latest value in microcoulombs (one decimal place). Each widget SHALL include a rolling time-series graph of recent readings. The voltage graph Y-axis SHALL be fixed from 2 V to 3 V with tick step 0.5 V. The charge graph Y-axis SHALL be fixed from 500 µC to 600 µC with tick step 50 µC. Graphs SHALL NOT include dashed asymptote reference lines. Graphs SHALL mark phase transitions with points when charge or discharge paths turn on (green dot for **Charge on**, yellow dot for **Discharge on**). The page SHALL display the current phase label **Charging** or **Discharging** when phase markers have been received. A sidebar SHALL provide navigation to other dashboard pages including Condensator. Connection status SHALL be shown as **Online** / **Offline** in the top-right corner. Notifications SHALL use custom toasts, not browser alerts.

#### Scenario: Voltage updates on Condensator page

- **WHEN** a WebSocket client on `/condensator` receives a condensator measurement broadcast
- **THEN** the Voltage widget updates to show the new value in V and appends a point to the voltage graph

#### Scenario: Charge Q updates on Condensator page

- **WHEN** a WebSocket client on `/condensator` receives a condensator measurement broadcast
- **THEN** the Charge Q widget updates to show the new value in µC and appends a point to the charge graph

#### Scenario: Phase label updates on Condensator page

- **WHEN** a WebSocket client on `/condensator` receives a condensator_phase broadcast
- **THEN** the page phase label updates to Charging or Discharging accordingly

#### Scenario: Voltage graph uses fixed Y-axis range

- **WHEN** a user views the Condensator page
- **THEN** the voltage graph Y-axis displays from 2 V to 3 V with 0.5 V tick marks

#### Scenario: Charge graph uses fixed Y-axis range

- **WHEN** a user views the Condensator page
- **THEN** the charge graph Y-axis displays from 500 µC to 600 µC with 50 µC tick marks

#### Scenario: Navigation includes Condensator

- **WHEN** a user opens any existing dashboard page
- **THEN** the sidebar includes a link to `/condensator`

### Requirement: WebSocket cached condensator state on connect

When a WebSocket client connects, the server SHALL send the last known condensator measurement and phase (if available) with `"cached": true`, using the same pattern as valve and mux cached messages.

#### Scenario: Connect receives cached condensator measurement

- **WHEN** a client connects to `/ws` after a condensator measurement line has been parsed
- **THEN** the client receives `{"type": "condensator", "v": <float>, "q_uc": <float>, "cached": true}`

#### Scenario: Connect receives cached condensator phase

- **WHEN** a client connects to `/ws` after a condensator phase marker has been parsed
- **THEN** the client receives `{"type": "condensator_phase", "phase": "<charging|discharging>", "cached": true}`

### Requirement: Condensator automated tests

The project SHALL include automated tests for the condensator feature. Python tests in `pytest/test_condensator.py` SHALL cover serial parsers, the `/condensator` route, status API fields, and cached WebSocket messages. EpoxyDuino AUnit tests in `arduino-tests/test_condensator/` SHALL cover shared logic in `arduino/condensator_logic.h`. The production sketch at `arduino/condensator/` SHALL include co-located Wokwi integration assets (`diagram.json`, `wokwi.toml`, `condensator.integration.yaml`) that exercise charge and discharge serial output in simulation. CI SHALL run condensator Python tests, AUnit tests, sketch compilation, and Wokwi integration tests with `WOKWI_SKETCH=condensator`.

#### Scenario: CI runs condensator test suite

- **WHEN** CI executes the project workflow
- **THEN** it runs `pytest/test_condensator.py`, `arduino-tests/test_condensator`, compiles `arduino/condensator`, and runs Wokwi integration for the condensator sketch
