#!/usr/bin/env bash
set -euo pipefail

FQBN="${FQBN:-arduino:avr:uno}"
TIMEOUT_MS="${TIMEOUT_MS:-45000}"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ARDUINO_DIR="$REPO_ROOT/arduino"
ARDUINO_TESTS_DIR="$REPO_ROOT/arduino-tests"
INCLUDE_FLAG="-I$ARDUINO_DIR"

if ! command -v arduino-cli >/dev/null 2>&1; then
  echo "arduino-cli not found on PATH" >&2
  exit 1
fi

if ! command -v wokwi-cli >/dev/null 2>&1; then
  echo "wokwi-cli not found on PATH" >&2
  exit 1
fi

if [[ -z "${WOKWI_CLI_TOKEN:-}" ]]; then
  echo "WOKWI_CLI_TOKEN is not set. Create a token at https://wokwi.com/dashboard/ci" >&2
  exit 1
fi

if ! arduino-cli core list 2>&1 | grep -q "arduino:avr"; then
  arduino-cli core update-index
  arduino-cli core install arduino:avr
fi

arduino-cli lib install "AUnit" || true

failed=()

for project in "$ARDUINO_TESTS_DIR"/test_*/; do
  name="$(basename "$project")"
  build_dir="$project/build"
  echo "==== $name ===="
  echo "Compiling $name..."
  if ! arduino-cli compile -b "$FQBN" "$project" \
    --build-property "compiler.cpp.extra_flags=$INCLUDE_FLAG" \
    --output-dir "$build_dir"; then
    failed+=("$name (compile)")
    continue
  fi

  echo "Running Wokwi simulation for $name..."
  log_file="$project/wokwi-report.log"
  if (
    cd "$project"
    wokwi-cli . --scenario aunit.test.yaml --timeout "$TIMEOUT_MS" --serial-log-file wokwi-report.log
  ); then
    echo "PASS: $name (report: $log_file)"
  else
    failed+=("$name (wokwi)")
    echo "FAIL: $name (see $log_file)" >&2
  fi
done

if ((${#failed[@]} > 0)); then
  echo "Wokwi tests failed: ${failed[*]}" >&2
  exit 1
fi

echo "All Wokwi AUnit tests passed."
