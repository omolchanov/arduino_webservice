#!/usr/bin/env bash
set -euo pipefail

FQBN="${FQBN:-arduino:avr:uno}"
TIMEOUT_MS="${TIMEOUT_MS:-60000}"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ARDUINO_DIR="$REPO_ROOT/arduino"
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

failed=()

for toml in "$ARDUINO_DIR"/*/wokwi.toml; do
  [[ -f "$toml" ]] || continue
  sketch_dir="$(dirname "$toml")"
  name="$(basename "$sketch_dir")"
  scenario="$(find "$sketch_dir" -maxdepth 1 -name '*.integration.yaml' -print -quit)"

  if [[ -z "$scenario" ]]; then
    echo "SKIP: $name (no *.integration.yaml)" >&2
    continue
  fi

  scenario_name="$(basename "$scenario")"
  build_dir="$sketch_dir/build"
  log_file="$sketch_dir/wokwi-report.log"

  echo "==== $name ===="
  echo "Compiling $name..."
  if ! arduino-cli compile -b "$FQBN" "$sketch_dir" \
    --build-property "compiler.cpp.extra_flags=$INCLUDE_FLAG" \
    --output-dir "$build_dir"; then
    failed+=("$name (compile)")
    continue
  fi

  echo "Validating diagram.json..."
  if ! (cd "$sketch_dir" && wokwi-cli lint); then
    failed+=("$name (diagram lint)")
    continue
  fi

  echo "Uploading diagram.json and firmware to Wokwi Simulation API..."
  wokwi_exit=0
  (
    cd "$sketch_dir"
    wokwi-cli . \
      --scenario "$scenario_name" \
      --timeout "$TIMEOUT_MS" \
      --serial-log-file wokwi-report.log
  ) || wokwi_exit=$?

  if [[ "$wokwi_exit" -ne 0 ]]; then
    failed+=("$name (wokwi)")
    echo "FAIL: $name (see $log_file)" >&2
  else
    echo "PASS: $name (report: $log_file)"
  fi
done

if ((${#failed[@]} > 0)); then
  echo "Wokwi integration tests failed: ${failed[*]}" >&2
  exit 1
fi

echo "All Wokwi integration tests passed."
