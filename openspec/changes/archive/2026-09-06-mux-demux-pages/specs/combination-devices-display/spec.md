## MODIFIED Requirements

### Requirement: One sketch per Combination Devices dashboard

The Multiplexor dashboard SHALL be driven exclusively by the dedicated firmware at `arduino/mux/mux.ino`. The system SHALL NOT require or support combining this dashboard with other sensor, valve, or keypad sketches in a single firmware upload.

#### Scenario: User runs Multiplexor dashboard

- **WHEN** the user wants to view the Multiplexor dashboard at `/multiplexor`
- **THEN** the user uploads `arduino/mux/mux.ino` to the Arduino (not `demux.ino`, `valves.ino`, `sensors.ino`, `simple01.ino`, or keypad firmware)

### Requirement: Combination Devices dashboard page

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

### Requirement: Combination Devices navigation link

All dashboard pages SHALL include sidebar links to `/multiplexor` labeled **Multiplexor** and to `/demultiplexor` labeled **Demultiplexor**. The Combination Devices link and `/combination` route SHALL NOT be used.

#### Scenario: Nav link on Keypad page

- **WHEN** a user views the Keypad page at `/`
- **THEN** the sidebar includes a link to `/multiplexor` and a link to `/demultiplexor`

## REMOVED Requirements

### Requirement: Combination Devices dashboard page

**Reason**: Replaced by dedicated Multiplexor page at `/multiplexor`.

**Migration**: Update bookmarks and links from `/combination` to `/multiplexor`.
