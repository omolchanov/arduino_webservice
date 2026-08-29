## 1. Frontend — value widget and layout

- [x] 1.1 Change `.value-widgets-row` to `grid-template-columns: repeat(5, 1fr)` and verify five cards fit in one row on `/digital`
- [x] 1.2 Add **Logic signal LED** value card as the fifth item in `.value-widgets-row` with status dot, `#logicSignalValue` element, and **signal** unit label; verify markup matches pot/detected/current/resistance card structure
- [x] 1.3 Register `logic` in the `widgets` object with `#logicSignalDot` and remove standalone `setLogicDot` / `clearLogicTimers` / `startLogicInitTimeout` / `applyLogicReading`; verify logic dot follows the same online/offline/init-timeout behavior as the other four widgets

## 2. Frontend — logic value wiring

- [x] 2.1 Update `setLogic()` to write to the new value widget element (display `0` or `1` only, no inline label); verify `handleLogic` and WebSocket `logic` events update the value widget
- [x] 2.2 Route `applyWidgetReading("logic", live)` from `handleLogic` and ensure `pollStatus` seeds from `last_logic_value`; verify cached status on page load shows the last value in the widget

## 3. Frontend — history graph card

- [x] 3.1 Remove `.logic-current` inline value block from the logic history card; rename header to **Logic signal LED history** without a status dot; verify the card shows chart only like other history cards
- [x] 3.2 Confirm `handleLogic` still appends history points and Clear button still clears logic history; verify graph steps between 0 and 1 when Arduino sends `Signal:` updates

## 4. Manual verification

- [x] 4.1 With `arduino/simple01.ino` flashed, Serial Monitor closed, and uvicorn running, open `/digital` and verify all five live widgets update live and the logic signal value toggles when the button changes D8 state
