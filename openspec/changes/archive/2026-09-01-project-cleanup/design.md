## Context

See proposal.md for motivation. The repo currently has:
- 15 stale Arduino build artifacts in `arduino-tests/**/build/` (`.elf`, `.hex`, `.bin`, `.eep`)
- `.pytest_cache/` directory present locally but not in `.gitignore`
- `__pycache__/` directories in `pytest/` and `scripts/` (already gitignored)
- Build artifact filenames don't match current test names (leftover from `redo-arduino-test-suite`)

## Goals / Non-Goals

**Goals:**
- Remove all local build artifacts and cache directories
- Make `.gitignore` comprehensive for all known temporary/generated file patterns
- Prevent future accidental commits of generated files

**Non-Goals:**
- Restructuring the project layout
- Modifying any source code, sketches, or tests
- Changing the build system or Makefiles

## Decisions

### 1. Delete local artifacts rather than just gitignore them
**Choice**: Delete the files from disk, not just add ignore rules.
**Rationale**: The build artifacts are stale (mismatched names from a prior refactor). Keeping them risks confusion. They are fully regenerable via `make -C arduino-tests`.
**Alternative**: Only update `.gitignore` — rejected because stale artifacts with wrong names could confuse future debugging.

### 2. Extend `.gitignore` with common patterns
**Choice**: Add `.pytest_cache/`, `*.o`, `*.d`, `*.out` (EpoxyDuino intermediates), and IDE patterns.
**Rationale**: EpoxyDuino builds produce `.o` and `.d` files alongside `.elf`. IDE artifacts (`.vscode/`, `.idea/`) are already absent but should be prevented. `.pytest_cache/` is actively generated but not ignored.
**Alternative**: Minimal addition of just `.pytest_cache/` — rejected because a single comprehensive pass is simpler than revisiting later.

## Risks / Trade-offs

- **[Stale build cache]** → After deleting `build/` directories, the next `make -C arduino-tests` will rebuild from scratch. This is a one-time cost (~seconds).
- **[Overly broad gitignore]** → Adding `*.o` and `*.d` globally could theoretically hide a file someone intended to track. Mitigated by scoping these patterns under `arduino-tests/` only.
