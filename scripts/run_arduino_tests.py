import os
import subprocess
import sys
import time
from pathlib import Path

import serial

REPO_ROOT = Path(__file__).resolve().parents[1]
ARDUINO_DIR = REPO_ROOT / "arduino"
TESTS_DIR = REPO_ROOT / "arduino-tests"
FQBN = "arduino:avr:uno"
INCLUDE_FLAG = f"-I{ARDUINO_DIR}"


def stop_uvicorn(force: bool = False) -> None:
    if sys.platform != "win32":
        return
    if not force and os.environ.get("RUN_ARDUINO_TESTS_SKIP_STOP"):
        return
    my_pid = os.getpid()
    kill_cmd = (
        f"$me={my_pid}; "
        "Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue | "
        "ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }; "
        "Get-CimInstance Win32_Process -Filter \"name='uvicorn.exe' OR name='python.exe'\" | "
        "Where-Object { "
        "$_.ProcessId -ne $me -and "
        "$_.CommandLine -match 'uvicorn|main:app|multiprocessing\\.spawn' "
        "} | ForEach-Object { "
        "Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue "
        "}"
    )
    for _ in range(3):
        subprocess.run(
            ["powershell", "-NoProfile", "-Command", kill_cmd],
            check=False,
        )
        time.sleep(1.0)
    time.sleep(2.0)


def wait_for_port(port: str, attempts: int = 60) -> bool:
    for _ in range(attempts):
        try:
            ser = serial.Serial(port, 9600, timeout=1)
            ser.dtr = False
            ser.rts = False
            ser.close()
            time.sleep(0.5)
            return True
        except serial.SerialException:
            time.sleep(0.5)
    return False


def read_aunit_summary(port: str, timeout: float = 45.0) -> int:
    if not wait_for_port(port, attempts=40):
        stop_uvicorn(force=True)
        wait_for_port(port, attempts=40)
    runner = REPO_ROOT / "scripts" / "read_aunit_serial.py"
    result = subprocess.run(
        [sys.executable, str(runner), port, str(int(timeout))],
        cwd=REPO_ROOT,
    )
    time.sleep(8.0)
    return result.returncode


def upload_test(sketch_dir: Path, port: str, attempts: int = 5) -> bool:
    if not wait_for_port(port):
        stop_uvicorn(force=True)
        if not wait_for_port(port, attempts=40):
            return False
    cmd = [
        "arduino-cli",
        "compile",
        "-b",
        FQBN,
        "-p",
        port,
        "-u",
        str(sketch_dir),
        "--build-property",
        f"compiler.cpp.extra_flags={INCLUDE_FLAG}",
    ]
    for attempt in range(attempts):
        result = subprocess.run(cmd, cwd=REPO_ROOT)
        if result.returncode == 0:
            time.sleep(4.0)
            return True
        time.sleep(3.0)
    return False


def main() -> int:
    port = sys.argv[1] if len(sys.argv) > 1 else "COM8"
    stop_uvicorn()
    projects = sorted(TESTS_DIR.glob("test_*"))
    if not projects:
        print("No test projects found", file=sys.stderr)
        return 1

    failed = False
    for project in projects:
        print(f"\n=== {project.name} ===", flush=True)
        if not upload_test(project, port):
            print(f"FAILED upload: {project.name}", file=sys.stderr)
            failed = True
            continue
        if read_aunit_summary(port) != 0:
            print(f"FAILED tests: {project.name}", file=sys.stderr)
            failed = True
        else:
            print(f"PASSED: {project.name}", flush=True)

    if failed:
        return 1
    print("\nAll arduino-tests passed.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
