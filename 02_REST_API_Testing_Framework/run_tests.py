







from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent
REPORTS_DIR = ROOT / "reports"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run pytest and save reports in a timestamped folder."
    )
    parser.add_argument(
        "pytest_args",
        nargs="*",
        help="Optional pytest arguments, for example tests/test_posts.py",
    )
    parser.add_argument(
        "-m",
        "--marker",
        help='Run only tests matching a marker expression, e.g. "posts" or "contract or headers".',
    )
    args = parser.parse_args()

    
    timestamp = datetime.now().astimezone().strftime("%Y-%m-%d_%H-%M-%S")
    run_dir = REPORTS_DIR / timestamp
    suffix = 1
    while run_dir.exists():
        run_dir = REPORTS_DIR / f"{timestamp}_{suffix}"
        suffix += 1

    allure_dir = run_dir / "allure"
    html_report = run_dir / "report.html"
    allure_dir.mkdir(parents=True, exist_ok=False)

    command = [
        sys.executable,
        "-m",
        "pytest",
        "-v",
        f"--html={html_report}",
        "--self-contained-html",
        f"--alluredir={allure_dir}",
    ]
    if args.marker:
        command.extend(["-m", args.marker])
    command.extend(args.pytest_args)

    print(f"\nReports folder: {run_dir.relative_to(ROOT)}")
    print(f"HTML report:    {html_report.relative_to(ROOT)}")
    print(f"Allure results: {allure_dir.relative_to(ROOT)}\n")
    print("=" * 72)
    result = subprocess.run(command, cwd=ROOT)
    print("\n" + "=" * 72)
    print(f"Pytest exit code: {result.returncode}")
    print(f"HTML report saved to: {html_report}")
    print(f"Raw Allure results saved to: {allure_dir}")
    print("\nTo open the HTML report, open report.html in your browser.")
    print(
        "To render the interactive Allure report (if Allure CLI is installed), run:\n"
        f"  allure serve \"{allure_dir}\""
    )
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
