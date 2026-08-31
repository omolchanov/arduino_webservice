import sys
import time

import serial


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python read_aunit_serial.py COM8 [timeout_seconds]", file=sys.stderr)
        return 2

    port = sys.argv[1]
    timeout = float(sys.argv[2]) if len(sys.argv) > 2 else 30.0
    deadline = time.time() + timeout

    ser = None
    for _ in range(60):
        try:
            ser = serial.Serial(port, 9600, timeout=1)
            break
        except serial.SerialException:
            time.sleep(0.5)
    if ser is None:
        print(f"Could not open {port} after retries", file=sys.stderr)
        return 1

    with ser:
        time.sleep(2.5)
        while time.time() < deadline:
            raw = ser.readline()
            if not raw:
                continue
            line = raw.decode("utf-8", errors="replace").strip()
            if not line:
                continue
            print(line)
            lower = line.lower()
            if "testrunner summary:" in lower:
                if "0 failed" in lower:
                    return 0
                return 1

    print(f"Timed out after {timeout}s waiting for AUnit results on {port}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
