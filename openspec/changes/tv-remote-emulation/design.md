## Context

See [proposal.md](proposal.md). The project uses one Arduino sketch per dashboard, 9600 baud newline-terminated serial, regex parsing in `main.py`, and WebSocket push to self-contained HTML pages. The Keypad page (`static/index.html`) already shows a last-key widget and scrolling history for matrix keypad input. No IR receiver code exists yet. This change adds IR decoding firmware and a TV-themed read-only dashboard.

## Goals / Non-Goals

**Goals:**

- New sketch `arduino/tv_remote/tv_remote.ino` decoding NEC-style IR from a receiver on D2
- Serial line format `Remote: <label>` (with optional hex suffix for unknown codes)
- TV Remote page at `/tv-remote` reusing Keypad layout patterns (last key, history, online badge, custom toasts)
- Backend parser, WebSocket `remote` events, status API, cached connect snapshot
- AUnit tests for label mapping; pytest for parser, route, API, WebSocket

**Non-Goals:**

- Physical TV/HDMI output or on-screen channel simulation
- Teaching mode for arbitrary remotes (fixed button map only)
- Serial write from browser
- Combining TV-remote firmware with other sketches

## Decisions

### Sketch and hardware

- **Decision:** `arduino/tv_remote/tv_remote.ino`; IR receiver signal on **D2** (interrupt-capable pin); use **IRremote** library (`arduino-cli lib install "IRremote"`)
- **Rationale:** D2 is the conventional choice for IRremote on Uno; library handles NEC decode for common TV remotes
- **Alternative:** Raw timing without library — rejected; more fragile and harder to test

### Shared logic header

- **Decision:** `arduino/tv_remote_logic.h` with `remoteLabelForCode(uint32_t code)` returning a string label; sketch calls it after decode
- **Rationale:** Matches `mux_logic.h` / `demux_logic.h` pattern; enables EpoxyDuino unit tests without hardware
- **Alternative:** Inline mapping in `.ino` only — rejected; no testable pure logic

### Serial line format

- **Decision:** Known buttons: `Remote: <LABEL>` (e.g. `Remote: POWER`, `Remote: 5`, `Remote: VOL+`). Unknown NEC codes: `Remote: UNKNOWN (0xAABBCCDD)`. Boot banner: `Remote ready` (ignored, like `Keypad ready`)
- **Rationale:** Human-readable labels for the TV UI; hex only when unmapped; distinct prefix avoids collision with keypad `Pressed:` lines
- **Alternative:** Hex-only lines — rejected; poor UX on TV dashboard

### Python regex and parser

- **Decision:** `REMOTE_PATTERN = re.compile(r"^Remote:\s+(.+?)(?:\s+\(0x([0-9A-Fa-f]+)\))?$")` → label string + optional code int; `parse_remote_line()` returns `tuple[str, int | None] | None`
- **Rationale:** Tolerant of labels with spaces (`VOL +` if needed); captures hex when present
- **Alternative:** Reuse keypad `parse_key_line` — rejected; different semantics and event shape

### WebSocket event shape

- **Decision:** `{"type": "remote", "key": "<label>", "code": <int|null>}`; omit `code` or set `null` when not present
- **Rationale:** Parallel to `{"type": "key", "key": "5"}` but distinct type so TV page filters correctly
- **Alternative:** Reuse `type: "key"` — rejected; mixes IR labels with keypad chars

### Status API fields

- **Decision:** `last_remote_key` (string|null), `last_remote_code` (int|null)
- **Rationale:** Supports last-key display and optional raw-code widget

### Parser placement in `read_serial`

- **Decision:** Check `REMOTE_PATTERN` after display/clock parsers, before keypad `parse_key_line`
- **Rationale:** `Remote:` prefix is unique; keypad single-char fallback must not mis-parse

### Route and page

- **Decision:** `GET /tv-remote` → `static/tv_remote.html`; nav label **TV Remote**; active accent **sky** `#38bdf8`
- **Rationale:** Distinct from keypad green accent; URL matches kebab-case convention (`/demultiplexor`)

### TV page UI

- **Decision:** Reuse Keypad card layout: **Last Button** (large label), **Recent Buttons** (history list, max 50), optional **Raw Code** subtext when `code` is present; page title **TV Remote**; subtitle notes sketch requirement (`tv_remote.ino`)
- **Rationale:** User asked to reference existing widgets; minimal new CSS
- **Alternative:** Full graphical remote pad — deferred; can highlight last label in a static button grid as stretch goal in tasks

### Navigation updates

- **Decision:** Add `<a href="/tv-remote">TV Remote</a>` to sidebar of all `static/*.html` pages after Demultiplexor link
- **Rationale:** Consistent with mux/demux nav rollout

### Tests

- **Decision:** `pytest/test_tv_remote.py` for parser, `/tv-remote` route, status API, WebSocket cache; `arduino-tests/test_tv_remote/` for label mapping
- **Rationale:** Same split as mux/demux change

### Wokwi integration (optional)

- **Decision:** Defer Wokwi `diagram.json` / `*.integration.yaml` unless apply time allows; not blocking for MVP
- **Rationale:** IR remote simulation in Wokwi is non-trivial; compile + unit tests suffice for CI

## Risks / Trade-offs

- **[Risk] Remote model mismatch** → Many buttons show `UNKNOWN (0x…)`; mitigated by documenting supported remote and allowing hex display
- **[Risk] Wrong sketch uploaded** → Page stays offline with empty widgets; mitigated by subtitle and spec one-sketch rule
- **[Risk] IRremote library version API drift** → Pin documented version in AGENTS.md; CI compile catches breaks
- **[Trade-off] Repeat codes while button held** → IRremote sends repeats; firmware debounces or filters `REPEAT` to avoid history spam (ignore consecutive identical within 300 ms)

## Migration Plan

1. Implement on `feature-tv-remote-emulation` branch
2. `arduino-cli lib install "IRremote"` locally and in CI compile step if needed
3. User flashes `arduino/tv_remote/tv_remote.ino`, opens `/tv-remote`
4. No breaking API changes; existing pages unchanged except nav link

## Open Questions

None.
