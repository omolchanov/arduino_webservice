## Context

See [proposal.md](proposal.md). The Digital Signal dashboard at `/digital` already receives logic signal data (`Signal: 0|1` from D8) via WebSocket `logic` events and `GET /api/status` (`last_logic_value`). Four live value widgets share a `.value-widgets-row` with `grid-template-columns: repeat(4, 1fr)`. Logic signal is the only measurement shown inline inside its history graph card, with separate dot/timer logic duplicated outside the `widgets` registry.

## Goals / Non-Goals

**Goals:**

- Add a fifth live value widget for Logic signal LED consistent with pot/detected/current/resistance cards
- Display all five widgets in one horizontal row on typical desktop widths
- Consolidate logic status-dot lifecycle into the existing `widgets` object
- Make the logic history graph card chart-only like the other history cards

**Non-Goals:**

- Backend, serial parsing, or API changes
- Renaming or reordering history graph cards
- Responsive breakpoints below desktop (existing overflow/scroll behavior is sufficient)
- Changing logic graph history buffer, Clear button, or localStorage keys

## Decisions

### 1. Frontend-only change

**Choice:** No `main.py` changes.

**Rationale:** `notify_logic`, `last_logic_value`, WebSocket cache-on-connect, and status polling already feed the UI. The gap is layout and widget registration only.

**Alternative considered:** New API field — rejected as redundant.

### 2. Fifth column in `.value-widgets-row`

**Choice:** Change CSS from `repeat(4, 1fr)` to `repeat(5, 1fr)`.

**Rationale:** Matches user request and resistance-widget spec pattern (“same row as … widgets”), extended to five columns.

**Alternative considered:** Wrap to two rows on narrow screens — rejected; out of scope and not requested.

### 3. Widget card pattern

**Choice:** New card in `.value-widgets-row` with header **Logic signal LED**, status dot, large `0`/`1` value, and unit label **signal** (matching detected’s **detected** label style). Reuse `.logic-value` color (`#fbbf24`).

**Rationale:** Visual parity with detected logic LED widget; distinguishes button-driven D8 signal from pot-derived D9 detected state.

**Alternative considered:** Label unit as “generated” — rejected; outdated terminology from pre-`Signal:` serial format.

### 4. Unify dot handling via `widgets.logic`

**Choice:** Register `logic` in the `widgets` object; remove `setLogicDot`, `clearLogicTimers`, `startLogicInitTimeout`, and `applyLogicReading` in favor of `applyWidgetReading("logic", live)` and shared online/offline helpers.

**Rationale:** One code path for all five widgets; graph card header loses its dot (history graphs for pot/current/resistance/detected have no dots).

### 5. Graph card simplification

**Choice:** Remove `.logic-current` block from the history card; title **Logic signal LED history** (no status dot). Graph still updates on `logic` WebSocket events via existing `handleLogic`.

**Rationale:** Matches other history cards; live value lives only in the value widget.

## Risks / Trade-offs

- **[Risk] Five columns may feel cramped below ~1200px width** → Acceptable; cards use `min-width: 0` and content area scrolls horizontally if needed.
- **[Risk] Duplicate logic dot removal may miss an edge case in online/offline transitions** → Mitigate by routing logic through the same `widgets` helpers already proven for four widgets.
- **[Trade-off] Value widget and graph both react to the same `logic` event** → Intentional; value updates immediately, graph appends history point (same as detected).

## Migration Plan

1. Edit `static/digital.html` only.
2. Reload `/digital` in browser; no server restart required unless already running stale assets.
3. Rollback: revert `digital.html` — no data migration.
