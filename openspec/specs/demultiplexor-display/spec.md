# demultiplexor-display Specification

## Purpose

Read 1-to-2 demultiplexer state (address A, data input DI, outputs Y0/Y1 on D11/D12) from the dedicated `arduino/demux/demux.ino` sketch over USB serial and display live widgets plus a highlighted truth table on a Demultiplexor dashboard.

## Requirements

### Requirement: One sketch per Demultiplexor dashboard

The Demultiplexor dashboard SHALL be driven exclusively by the dedicated firmware at `arduino/demux/demux.ino`. The system SHALL NOT require or support combining this dashboard with other sketches in a single firmware upload.

#### Scenario: User runs Demultiplexor dashboard

- **WHEN** the user wants to view the Demultiplexor dashboard at `/demultiplexor`
- **THEN** the user uploads `arduino/demux/demux.ino` to the Arduino (not `mux.ino`, `valves.ino`, or other production sketches)

### Requirement: DEMUX status serial ingestion

The system SHALL read DEMUX status lines from `arduino/demux/demux.ino` over USB serial at 9600 baud. Lines matching `A=<0|1>  DI=<0|1>  ->  Y0=<0|1>  Y1=<0|1>` (with optional trailing text such as `(selected: Y0)`) SHALL be parsed and broadcast to all connected WebSocket clients as JSON `{"type": "demux", "a": <0|1>, "di": <0|1>, "y0": <0|1>, "y1": <0|1>}`.

#### Scenario: DEMUX status line received

- **WHEN** the Arduino sends `A=0  DI=1  ->  Y0=1  Y1=0  (selected: Y0)` over serial
- **THEN** the server broadcasts `{"type": "demux", "a": 0, "di": 1, "y0": 1, "y1": 0}` to all connected WebSocket clients

#### Scenario: DEMUX status line with A=1

- **WHEN** the Arduino sends `A=1  DI=1  ->  Y0=0  Y1=1  (selected: Y1)` over serial
- **THEN** the server broadcasts `{"type": "demux", "a": 1, "di": 1, "y0": 0, "y1": 1}` to all connected WebSocket clients

#### Scenario: Invalid DEMUX line ignored

- **WHEN** the serial port sends a line that does not match the DEMUX status format
- **THEN** the server does not broadcast a demux event (may still parse as mux, valve, or other applicable formats)

### Requirement: DEMUX values in status API

`GET /api/status` SHALL include `last_demux_a`, `last_demux_di`, `last_demux_y0`, and `last_demux_y1` as integers `0`, `1`, or `null` when no reading has been received.

#### Scenario: Status includes last DEMUX values

- **WHEN** a client requests `GET /api/status` after a DEMUX status line has been parsed
- **THEN** the response includes `"last_demux_a": 0`, `"last_demux_di": 1`, `"last_demux_y0": 1`, and `"last_demux_y1": 0` (or corresponding values from the last reading)

### Requirement: Demultiplexor dashboard page

The system SHALL serve a Demultiplexor dashboard at `GET /demultiplexor` from `static/demultiplexor.html`. The page SHALL reuse the same visual patterns as the Multiplexor and Valves dashboards (sidebar navigation, dark theme, card layout, online/offline status badge, custom toast notifications).

#### Scenario: Demultiplexor page loads

- **WHEN** a user navigates to `/demultiplexor`
- **THEN** the browser displays the Demultiplexor dashboard with sidebar navigation including links to Keypad, Sensors, Digital Signal, Valves, Display, Multiplexor, and Demultiplexor

### Requirement: Address widget

The Demultiplexor dashboard SHALL include a widget displaying address input **A** (D4) from live serial data, with a status dot following the same online/offline and pending-reading pattern as the Multiplexor dashboard.

#### Scenario: Address widget updates on new reading

- **WHEN** the page receives a WebSocket `demux` event with `"a": 1`
- **THEN** the address widget displays `1` and the status dot shows ok

### Requirement: Data input widget

The Demultiplexor dashboard SHALL include a widget displaying data input **DI** (D2) from live serial data, with a status dot following the same online/offline and pending-reading pattern as the Multiplexor dashboard.

#### Scenario: Data input widget updates on new reading

- **WHEN** the page receives a WebSocket `demux` event with `"di": 1`
- **THEN** the data input widget displays `1`

### Requirement: Output widgets Y0 and Y1

The Demultiplexor dashboard SHALL include widgets displaying outputs **Y0** (D11) and **Y1** (D12) from live serial data, each with a status dot following the same online/offline and pending-reading pattern as the Multiplexor dashboard.

#### Scenario: Output widgets update on new reading

- **WHEN** the page receives a WebSocket `demux` event with `"y0": 1` and `"y1": 0`
- **THEN** the Y0 widget displays `1` and the Y1 widget displays `0`

### Requirement: DEMUX truth table with don't-care cells

The Demultiplexor dashboard SHALL display a truth table below the widgets with columns **A**, **DI**, **Y0**, and **Y1**. The table SHALL use **X** for don't-care output cells on the inactive branch (when A=0, Y1 is X; when A=1, Y0 is X). The table SHALL contain exactly four rows:

- 0, 0 → Y0=0, Y1=X
- 0, 1 → Y0=1, Y1=X
- 1, 0 → Y0=X, Y1=0
- 1, 1 → Y0=X, Y1=1

The row matching the current live inputs (A, DI) SHALL be visually highlighted using the same active-row styling as the Multiplexor truth table.

#### Scenario: Truth table highlights current inputs

- **WHEN** live inputs are A=0, DI=1
- **THEN** the truth table row for A=0, DI=1 is highlighted and shows Y0=1, Y1=X

#### Scenario: Truth table highlight moves when inputs change

- **WHEN** live inputs change from A=0, DI=1 to A=1, DI=1
- **THEN** the highlighted row updates to A=1, DI=1 with Y0=X, Y1=1

### Requirement: WebSocket cached DEMUX state on connect

When a WebSocket client connects, the server SHALL send the last known DEMUX state (if available) with `"cached": true`, using the same pattern as mux cached messages.

#### Scenario: Connect receives cached DEMUX state

- **WHEN** a client connects to `/ws` after a DEMUX status line has been parsed
- **THEN** the client receives `{"type": "demux", "a": <n>, "di": <n>, "y0": <n>, "y1": <n>, "cached": true}`

### Requirement: Demultiplexor navigation link

All dashboard pages SHALL include a sidebar link to `/demultiplexor` labeled **Demultiplexor**.

#### Scenario: Nav link on Keypad page

- **WHEN** a user views the Keypad page at `/`
- **THEN** the sidebar includes a link to `/demultiplexor`
