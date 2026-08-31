import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

TEST_LINE = re.compile(r"^Test (\S+) (passed|failed)\.", re.MULTILINE)
SUMMARY_LINE = re.compile(
    r"TestRunner summary:\s*(\d+) passed,\s*(\d+) failed", re.MULTILINE
)
STARTED_LINE = re.compile(r"TestRunner started on (\d+) test\(s\)\.")


def build_report(project_name: str, serial: str, wokwi_exit: int) -> tuple[str, bool]:
    tests = TEST_LINE.findall(serial)
    summary = SUMMARY_LINE.search(serial)
    started = STARTED_LINE.search(serial)

    lines = [
        f"=== Wokwi report: {project_name} ===",
        f"Timestamp: {datetime.now(timezone.utc).isoformat()}",
        f"Wokwi exit code: {wokwi_exit}",
        "",
        "--- Serial output ---",
        serial.rstrip(),
        "",
        "--- Per-test results ---",
    ]

    if tests:
        for name, status in tests:
            mark = "PASS" if status == "passed" else "FAIL"
            lines.append(f"  [{mark}] {name}")
    else:
        lines.append("  (no individual test results captured)")

    lines.append("")
    if summary:
        passed_count, failed_count = summary.groups()
        lines.append(f"Summary: {passed_count} passed, {failed_count} failed")
        overall = int(failed_count) == 0 and wokwi_exit == 0
    else:
        lines.append("Summary: (not found in serial output)")
        overall = False

    lines.append(f"Overall: {'PASS' if overall else 'FAIL'}")

    if started and tests:
        expected = int(started.group(1))
        if len(tests) != expected:
            lines.append(
                f"WARNING: expected {expected} tests, captured {len(tests)} in serial log"
            )
            overall = False

    return "\n".join(lines) + "\n", overall


def format_project_report(project_name: str, log_path: Path, wokwi_exit: int) -> bool:
    serial = log_path.read_text(encoding="utf-8", errors="replace") if log_path.exists() else ""
    report, overall = build_report(project_name, serial, wokwi_exit)
    log_path.write_text(report, encoding="utf-8")
    return overall


def append_suite_report(suite_path: Path, log_path: Path) -> None:
    body = log_path.read_text(encoding="utf-8", errors="replace") if log_path.exists() else ""
    block = f"\n{'=' * 60}\n{body.rstrip()}\n"
    with suite_path.open("a", encoding="utf-8") as f:
        f.write(block)


def init_suite_report(suite_path: Path) -> None:
    header = (
        f"=== Wokwi suite report ===\n"
        f"Timestamp: {datetime.now(timezone.utc).isoformat()}\n"
    )
    suite_path.write_text(header, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Format Wokwi AUnit report logs")
    parser.add_argument("--init-suite", action="store_true")
    parser.add_argument("--suite-report", type=Path, default=None)
    parser.add_argument("project_name", nargs="?")
    parser.add_argument("log_path", nargs="?", type=Path)
    parser.add_argument("wokwi_exit_code", nargs="?", type=int)
    args = parser.parse_args()

    if args.init_suite:
        if args.suite_report is None:
            parser.error("--init-suite requires --suite-report")
        init_suite_report(args.suite_report)
        return 0

    if not args.project_name or args.log_path is None or args.wokwi_exit_code is None:
        parser.error("project_name, log_path, and wokwi_exit_code are required")

    ok = format_project_report(args.project_name, args.log_path, args.wokwi_exit_code)
    if args.suite_report is not None:
        append_suite_report(args.suite_report, args.log_path)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
