# combination-devices-display Specification

## Purpose

Read 2-to-1 multiplexer state (address A, data inputs DI0/DI1, output DO on D13) from the dedicated `arduino/mux/mux.ino` sketch over USB serial and display live widgets plus a highlighted truth table on a Multiplexor dashboard.

## Requirements

### Requirement: One sketch per Multiplexor dashboard

The Multiplexor dashboard SHALL be driven exclusively by the dedicated firmware at `arduino/mux/mux.ino`. The system SHALL NOT require or support combining this dashboard with other sensor, valve, or keypad sketches in a single firmware upload.

#### Scenario: User runs Multiplexor dashboard

- **WHEN** the user wants to view the Multiplexor dashboard at `/multiplexor`
- **THEN** the user uploads `arduino/mux/mux.ino` to the Arduino (not `demux.ino`, `valves.ino`, `sensors.ino`, `simple01.ino`, or keypad firmware)

### Requirement: MUX status serial ingestion

The system SHALL read MUX status lines from `arduino/mux/mux.ino` over USB serial at 9600 baud. Lines matching `A=<0|1>  DI0=<0|1>  DI1=<0|1>  ->  DO=<0|1>` (with optional trailing text such as `(selected: DI0)`) SHALL be parsed and broadcast to all connected WebSocket clients as JSON `{"type": "mux", "a": <0|1>, "di0": <0|1>, "di1": <0|1>, "do": <0|1>}`.

#### Scenario: MUX status line received

- **WHEN** the Arduino sends `A=0  DI0=1  DI1=0  ->  DO=1  (selected: DI0)` over serial
- **THEN** the server broadcasts `{"type": "mux", "a": 0, "di0": 1, "di1": 0, "do": 1}` to all connected WebSocket clients

#### Scenario: MUX status line with A=1

- **WHEN** the Arduino sends `A=1  DI0=1  DI1=0  ->  DO=0  (selected: DI1)` over serial
- **THEN** the server broadcasts `{"type": "mux", "a": 1, "di0": 1, "di1": 0, "do": 0}` to all connected WebSocket clients

#### Scenario: Invalid MUX line ignored

- **WHEN** the serial port sends a line that does not match the MUX status format
- **THEN** the server does not broadcast a mux event (may still parse as demux, valve, distance, light, pot, or keypad if applicable)

### Requirement: MUX values in status API

`GET /api/status` SHALL include `last_mux_a`, `last_mux_di0`, `last_mux_di1`, and `last_mux_do` as integers `0`, `1`, or `null` when no reading has been received.

#### Scenario: Status includes last MUX values

- **WHEN** a client requests `GET /api/status` after a MUX status line has been parsed
- **THEN** the response includes `"last_mux_a": 0`, `"last_mux_di0": 1`, `"last_mux_di1": 0`, and `"last_mux_do": 1` (or corresponding values from the last reading)

### Requirement: Multiplexor dashboard page

The system SHALL serve a Multiplexor dashboard at `GET /multiplexor` from `static/multiplexor.html`. The page SHALL reuse the same visual patterns as the Valves and Digital Signal dashboards (sidebar navigation, dark theme, card layout, online/offline status badge, custom toast notifications).

#### Scenario: Multiplexor page loads

- **WHEN** a user navigates to `/multiplexor`
- **THEN** the browser displays the Multiplexor dashboard with sidebar navigation including links to Keypad, Sensors, Digital Signal, Valves, Display, Multiplexor, and Demultiplexor

### Requirement: Address widget

The Multiplexor dashboard SHALL include a widget displaying address input **A** from live serial data. The widget SHALL include a status dot following the same online/offline and pending-reading pattern as widgets on the Valves dashboard.

#### Scenario: Address widget updates on new reading

- **WHEN** the page receives a WebSocket `mux` event with `"a": 1`
- **THEN** the address widget displays `1` and the status dot shows ok

### Requirement: Data inputs widget

The Multiplexor dashboard SHALL include a widget displaying data inputs **DI0** and **DI1** from live serial data. The widget SHALL include a status dot following the same online/offline and pending-reading pattern as widgets on the Valves dashboard.

#### Scenario: Data inputs widget updates on new reading

- **WHEN** the page receives a WebSocket `mux` event with `"di0": 1` and `"di1": 0`
- **THEN** the data inputs widget displays DI0 as `1` and DI1 as `0`

### Requirement: Output widget (D13)

The Multiplexor dashboard SHALL include a widget displaying output **DO** (D13) from live serial data, labeled to indicate pin D13. The widget SHALL include a status dot following the same online/offline and pending-reading pattern as widgets on the Valves dashboard.

#### Scenario: Output widget updates on new reading

- **WHEN** the page receives a WebSocket `mux` event with `"do": 1`
- **THEN** the output widget displays `1` and indicates D13

### Requirement: MUX truth table

The Multiplexor dashboard SHALL display a truth table below the widgets with columns **A**, **DI0**, **DI1**, and **DO**. The table SHALL use **X** for don't-care data-input cells on the inactive branch (when A=0, DI1 is X; when A=1, DI0 is X). The table SHALL contain exactly four rows:

- 0, 0, X → 0
- 0, 1, X → 1
- 1, X, 0 → 0
- 1, X, 1 → 1

The row matching the current live inputs (A, and the active DI for the selected branch) SHALL be visually highlighted using the same active-row styling as the Valves truth table.

#### Scenario: Truth table highlights current inputs

- **WHEN** live inputs are A=0, DI0=1, DI1=0
- **THEN** the truth table row for A=0, DI0=1, DI1=X is highlighted and shows DO=1

#### Scenario: Truth table highlight moves when inputs change

- **WHEN** live inputs change from A=0, DI0=1, DI1=0 to A=1, DI0=1, DI1=0
- **THEN** the highlighted row updates to A=1, DI0=X, DI1=0 with DO=0

### Requirement: WebSocket cached MUX state on connect

When a WebSocket client connects, the server SHALL send the last known MUX state (if available) with `"cached": true`, using the same pattern as valve cached messages.

#### Scenario: Connect receives cached MUX state

- **WHEN** a client connects to `/ws` after a MUX status line has been parsed
- **THEN** the client receives `{"type": "mux", "a": <n>, "di0": <n>, "di1": <n>, "do": <n>, "cached": true}`

### Requirement: Multiplexor and Demultiplexor navigation links

All dashboard pages SHALL include sidebar links to `/multiplexor` labeled **Multiplexor** and to `/demultiplexor` labeled **Demultiplexor**. The Combination Devices link and `/combination` route SHALL NOT be used.

#### Scenario: Nav link on Keypad page

- **WHEN** a user views the Keypad page at `/`
- **THEN** the sidebar includes a link to `/multiplexor` and a link to `/demultiplexor`
