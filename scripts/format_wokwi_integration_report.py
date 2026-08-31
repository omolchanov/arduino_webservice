import argparse
import html
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SCENARIO_OK = re.compile(r"Scenario completed successfully", re.IGNORECASE)
SCENARIO_FAIL = re.compile(r"(FAIL|Error|Timeout|did not finish)", re.IGNORECASE)
MATCHED_LINE = re.compile(r"Expected text matched:\s*\"([^\"]+)\"", re.IGNORECASE)
WAIT_SERIAL_LINE = re.compile(r"^\s*-\s+wait-serial:\s*", re.MULTILINE)


def find_integration_scenario(sketch_dir: Path) -> Path | None:
    matches = sorted(sketch_dir.glob("*.integration.yaml"))
    return matches[0] if matches else None


def count_expected_serial_checks(scenario_path: Path | None) -> int:
    if scenario_path is None or not scenario_path.exists():
        return 0
    text = scenario_path.read_text(encoding="utf-8", errors="replace")
    return len(WAIT_SERIAL_LINE.findall(text))


def parse_cli_matches(cli_text: str) -> list[str]:
    return MATCHED_LINE.findall(cli_text)


def infer_status(serial: str, cli_text: str, wokwi_exit: int | None) -> bool:
    combined = f"{serial}\n{cli_text}"
    if wokwi_exit is not None and wokwi_exit != 0:
        return False
    if SCENARIO_OK.search(combined):
        return True
    if not serial.strip() and not cli_text.strip():
        return False
    if SCENARIO_FAIL.search(combined):
        return False
    return wokwi_exit == 0 if wokwi_exit is not None else False


def format_step_count(matched: int, expected: int) -> str:
    if expected > 0:
        return f"{matched}/{expected}"
    return str(matched)


def collect_reports(arduino_dir: Path) -> list[dict]:
    reports: list[dict] = []
    for log_path in sorted(arduino_dir.glob("*/wokwi-report.log")):
        sketch_dir = log_path.parent
        sketch = sketch_dir.name
        serial = log_path.read_text(encoding="utf-8", errors="replace")
        cli_path = sketch_dir / "wokwi-cli.log"
        cli_text = cli_path.read_text(encoding="utf-8", errors="replace") if cli_path.exists() else ""
        scenario_path = find_integration_scenario(sketch_dir)
        expected_checks = count_expected_serial_checks(scenario_path)
        status_path = sketch_dir / "wokwi-exit.code"
        wokwi_exit = None
        if status_path.exists():
            try:
                wokwi_exit = int(status_path.read_text(encoding="utf-8").strip())
            except ValueError:
                wokwi_exit = 1
        passed = infer_status(serial, cli_text, wokwi_exit)
        matches = parse_cli_matches(cli_text)
        reports.append(
            {
                "sketch": sketch,
                "log_path": log_path,
                "serial": serial,
                "cli_text": cli_text,
                "passed": passed,
                "matches": matches,
                "expected_checks": expected_checks,
                "wokwi_exit": wokwi_exit,
            }
        )
    return reports


def build_html(reports: list[dict]) -> str:
    overall = all(r["passed"] for r in reports) if reports else False
    status_label = "PASS" if overall else "FAIL"
    status_class = "pass" if overall else "fail"
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    rows = []
    for report in reports:
        mark = "PASS" if report["passed"] else "FAIL"
        row_class = "pass" if report["passed"] else "fail"
        steps = step_count_for_summary(report)
        rows.append(
            f"<tr class='{row_class}'>"
            f"<td>{html.escape(report['sketch'])}</td>"
            f"<td><strong>{mark}</strong></td>"
            f"<td>{html.escape(steps)}</td>"
            f"</tr>"
        )

    sections = []
    for report in reports:
        match_items = report["matches"]
        if not match_items and report["passed"] and report["expected_checks"] > 0:
            match_items = [
                f"All {report['expected_checks']} wait-serial checks passed (see scenario YAML)"
            ]
        sections.append(
            "<section>"
            f"<h2>{html.escape(report['sketch'])}</h2>"
            f"<p>Status: <strong>{'PASS' if report['passed'] else 'FAIL'}</strong></p>"
            "<h3>Matched serial expectations</h3>"
            "<ul>"
            + "".join(f"<li><code>{html.escape(m)}</code></li>" for m in match_items)
            + ("<li><em>None captured</em></li>" if not match_items else "")
            + "</ul>"
            "<h3>Firmware serial output</h3>"
            f"<pre>{html.escape(report['serial'].rstrip())}</pre>"
            + (
                "<h3>Wokwi CLI output</h3>"
                f"<pre>{html.escape(report['cli_text'].rstrip())}</pre>"
                if report["cli_text"].strip()
                else ""
            )
            + "</section>"
        )

    body = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Wokwi Integration Report</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 2rem; background: #0f1419; color: #e6edf3; }}
    h1 {{ margin-bottom: 0.25rem; }}
    .meta {{ color: #8b949e; margin-bottom: 1.5rem; }}
    .overall {{ display: inline-block; padding: 0.35rem 0.75rem; border-radius: 6px; font-weight: 700; }}
    .overall.pass {{ background: #238636; color: #fff; }}
    .overall.fail {{ background: #da3633; color: #fff; }}
    table {{ border-collapse: collapse; width: 100%; margin: 1rem 0 2rem; }}
    th, td {{ border: 1px solid #30363d; padding: 0.6rem 0.75rem; text-align: left; }}
    th {{ background: #161b22; }}
    tr.pass td:nth-child(2) {{ color: #3fb950; }}
    tr.fail td:nth-child(2) {{ color: #f85149; }}
    section {{ margin-bottom: 2rem; padding-bottom: 1rem; border-bottom: 1px solid #30363d; }}
    pre {{ background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 1rem; overflow-x: auto; white-space: pre-wrap; }}
    code {{ background: #161b22; padding: 0.1rem 0.3rem; border-radius: 4px; }}
  </style>
</head>
<body>
  <h1>Wokwi Integration Report</h1>
  <p class="meta">Generated {generated}</p>
  <p><span class="overall {status_class}">{status_label}</span></p>
  <table>
    <thead><tr><th>Sketch</th><th>Result</th><th>Serial checks</th></tr></thead>
    <tbody>
      {''.join(rows) if rows else "<tr><td colspan='3'><em>No reports found</em></td></tr>"}
    </tbody>
  </table>
  {''.join(sections)}
</body>
</html>
"""
    return body


def step_count_for_summary(report: dict) -> str:
    matched = len(report["matches"])
    if matched == 0 and report["passed"] and report["expected_checks"] > 0:
        matched = report["expected_checks"]
    return format_step_count(matched, report["expected_checks"])


def build_github_summary(reports: list[dict], html_path: Path) -> str:
    overall = all(r["passed"] for r in reports) if reports else False
    lines = [
        "## Wokwi integration report",
        "",
        f"**Overall:** {'PASS' if overall else 'FAIL'}",
        "",
        "| Sketch | Result | Serial checks |",
        "| --- | --- | --- |",
    ]
    for report in reports:
        mark = "PASS" if report["passed"] else "FAIL"
        lines.append(f"| {report['sketch']} | **{mark}** | {step_count_for_summary(report)} |")

    lines.extend(["", f"Full HTML report: `{html_path.as_posix()}` (also attached as a workflow artifact).", ""])

    for report in reports:
        lines.append(f"<details><summary><strong>{html.escape(report['sketch'])}</strong> firmware serial log</summary>")
        lines.append("")
        lines.append("```text")
        lines.append(report["serial"].rstrip() or "(empty)")
        lines.append("```")
        lines.append("")
        lines.append("</details>")
        lines.append("")

    return "\n".join(lines)


def write_github_summary(markdown: str) -> None:
    summary_file = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary_file:
        print(markdown)
        return
    with open(summary_file, "a", encoding="utf-8") as f:
        f.write(markdown)
        if not markdown.endswith("\n"):
            f.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Format Wokwi integration test reports")
    parser.add_argument(
        "--arduino-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "arduino",
    )
    parser.add_argument(
        "--html-out",
        type=Path,
        default=None,
        help="HTML report output path (default: <arduino-dir>/wokwi-integration-report.html)",
    )
    parser.add_argument(
        "--github-summary",
        action="store_true",
        help="Append markdown/HTML summary to GITHUB_STEP_SUMMARY",
    )
    args = parser.parse_args()

    reports = collect_reports(args.arduino_dir)
    html_out = args.html_out or (args.arduino_dir / "wokwi-integration-report.html")
    html_out.parent.mkdir(parents=True, exist_ok=True)
    html_out.write_text(build_html(reports), encoding="utf-8")

    if args.github_summary:
        write_github_summary(build_github_summary(reports, html_out))

    if not reports:
        print("No wokwi-report.log files found", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
