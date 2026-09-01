## Why

The repository has accumulated build artifacts, cache directories, and stale files that clutter the workspace. The `.gitignore` is incomplete — `.pytest_cache/` is present on disk but not ignored. Arduino test build directories contain artifacts with mismatched names from a prior naming scheme (`test_sensor_math.*` inside `test_sensors/build/`). Cleaning up now keeps the repo tidy and prevents accidental commits of generated files.

## What Changes

- Delete local build artifacts under `arduino-tests/**/build/` (stale `.elf`, `.hex`, `.bin`, `.eep` files)
- Delete local cache directories: `.pytest_cache/`, `__pycache__/`, `pytest/__pycache__/`, `scripts/__pycache__/`
- Update `.gitignore` to cover `.pytest_cache/` and other common temporary patterns
- Verify no tracked files need removal from git index

## Capabilities

### New Capabilities

_None — this is a pure cleanup with no new behavior._

### Modified Capabilities

_None — no spec-level behavior changes._

This change sets `skip_specs: true` (pure refactor/cleanup).

## Impact

- **Files removed**: ~24 local build artifacts and cache files (none tracked by git)
- **`.gitignore`**: Additional patterns added to prevent future clutter
- **No code changes**: No modifications to `main.py`, sketches, tests, or HTML
- **No API changes**: No endpoints affected
