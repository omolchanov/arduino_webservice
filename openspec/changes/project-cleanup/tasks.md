## 1. Delete stale build artifacts

- [x] 1.1 Delete `arduino-tests/test_sensors/build/` directory and verify it no longer exists
- [x] 1.2 Delete `arduino-tests/test_simple01/build/` directory and verify it no longer exists
- [x] 1.3 Delete `arduino-tests/test_valves/build/` directory and verify it no longer exists

## 2. Delete cache directories

- [x] 2.1 Delete `.pytest_cache/` from the project root and verify it no longer exists
- [x] 2.2 Delete `__pycache__/` from the project root and verify it no longer exists
- [x] 2.3 Delete `pytest/__pycache__/` and verify it no longer exists
- [x] 2.4 Delete `scripts/__pycache__/` and verify it no longer exists

## 3. Update .gitignore

- [x] 3.1 Add `.pytest_cache/` pattern to `.gitignore` and verify `git check-ignore .pytest_cache` returns a match
- [x] 3.2 Add EpoxyDuino intermediate patterns (`*.o`, `*.d`) scoped under `arduino-tests/` and verify `git check-ignore arduino-tests/test_valves/test_valves.o` returns a match
- [x] 3.3 Verify no tracked files are matched by the new ignore rules using `git ls-files -i --exclude-standard`
