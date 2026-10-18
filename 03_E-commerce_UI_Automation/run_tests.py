#!/usr/bin/env python3
"""Run all storefront test sections in sequence, with independent reports."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright

from config import BASE_URL, DISCOVERY_WAIT_MS, REPORTS_DIR, VIEWPORT
from ecomqa.browser import launch_chromium
from ecomqa.discovery import (
    VISIBLE_LINKS_SCRIPT,
    build_homepage_specs,
    discover_currency_cases,
)
from ecomqa.reporting import build_html_report
from ecomqa.collection_testing import SECTION_CONFIGS, discover_collection_section


def parse_args():
    parser = argparse.ArgumentParser(description="E-commerce UI Automation — sectioned test runner")
    parser.add_argument("--headless", action="store_true", help="Run Chromium without a visible window")
    parser.add_argument("--slowmo", type=int, default=50, help="Slow down browser actions in milliseconds (default: 50)")
    parser.add_argument("--url", default=BASE_URL, help="Homepage URL to test")
    parser.add_argument(
        "--section",
        choices=("all", "main", "tshirts", "mugs"),
        default="all",
        help="Run all sections (default), or only main, tshirts, or mugs.",
    )
    parser.add_argument("--report-dir", default=None, help="Custom report directory")
    return parser.parse_args()


def _normalise_url(value: str) -> str:
    value = value.strip()
    if not value:
        return BASE_URL
    return value if value.endswith("/") else value + "/"


def discover(base_url: str, headless: bool, slowmo: int, report_dir: Path) -> tuple[list[dict], dict]:
    discovery: dict = {
        "homepage": {"ok": False, "status": None, "url": base_url, "details": "Homepage discovery has not completed."},
        "links_discovered": 0,
        "currency": {"found": False, "details": "Currency selector has not been inspected."},
        "homepage_screenshot": None,
        "discovery_error": None,
    }
    specs: list[dict] = []
    try:
        with sync_playwright() as playwright:
            browser = launch_chromium(playwright, headless=headless, slow_mo=slowmo)
            context = browser.new_context(viewport=VIEWPORT, accept_downloads=True, reduced_motion="reduce")
            page = context.new_page()
            page.set_default_navigation_timeout(15_000)
            try:
                response = page.goto(base_url, wait_until="domcontentloaded", timeout=15_000)
                page.wait_for_timeout(DISCOVERY_WAIT_MS)
                status = response.status if response else None
                discovery["homepage"] = {
                    "ok": bool(response and status < 400),
                    "status": status,
                    "url": page.url,
                    "details": f"Homepage discovery response: HTTP {status if status is not None else 'no response'}; URL={page.url}",
                }
                links = page.evaluate(VISIBLE_LINKS_SCRIPT)
                discovery["links_discovered"] = len(links)
                specs = build_homepage_specs(links, base_url)

                screenshot_path = report_dir / "homepage-preview.png"
                try:
                    page.screenshot(path=str(screenshot_path), full_page=True, timeout=7_000)
                    discovery["homepage_screenshot"] = screenshot_path.name
                except Exception as exc:
                    discovery["homepage_screenshot_error"] = f"{type(exc).__name__}: {str(exc).splitlines()[0][:160]}"

                currency = discover_currency_cases(page, specs)
                detected_codes = sorted({str(case.get("currencyCode", "")).upper() for case in specs if case.get("kind") == "currency_option"})
                discovery["currency"] = {
                    "found": bool(currency.get("found")),
                    "count": len(detected_codes),
                    "codes": detected_codes,
                    "details": currency.get("details", "Currency selector inspection completed."),
                }
            finally:
                try:
                    context.close()
                except Exception:
                    pass
                try:
                    browser.close()
                except Exception:
                    pass
    except Exception as exc:
        discovery["discovery_error"] = f"{type(exc).__name__}: {str(exc).splitlines()[0][:300]}"
        discovery["homepage"]["details"] = "Homepage discovery failed: " + discovery["discovery_error"]
        if not specs:
            specs = build_homepage_specs([], base_url)
        if not any(item.get("kind") in ("currency_option", "currency_discovery") for item in specs):
            specs.append({
                "id": "currency-discovery", "kind": "currency_discovery",
                "label": "Currency selector and available currencies", "discovered": False,
                "discoveryNote": "Currency discovery could not run because the homepage/browser discovery failed.",
            })
        discovery["currency"] = {"found": False, "details": "Currency discovery could not run."}
    return specs, discovery


def main() -> int:
    args = parse_args()

    # The default command runs the complete suite, in order, with a separate report per section.
    # Each child process keeps its own discovery/specification/results files isolated.
    if args.section == "all":
        script = str(Path(__file__).resolve())
        sections = (
            ("main", "Section 01 — Main Page", "section-01-main"),
            ("tshirts", "Section 02 — T-shirt Collection", "section-02-tshirts"),
            ("mugs", "Section 03 — Mug Collection", "section-03-mugs"),
        )
        print("\n" + "=" * 88, flush=True)
        print(" E-COMMERCE UI AUTOMATION — COMPLETE TEST SUITE ".center(88, "="), flush=True)
        print("=" * 88, flush=True)
        failure_count = 0
        for section_key, section_title, report_folder in sections:
            command = [
                sys.executable, script,
                "--section", section_key,
                "--url", args.url,
                "--slowmo", str(max(0, args.slowmo)),
            ]
            if args.headless:
                command.append("--headless")
            if args.report_dir:
                target_report_dir = Path(args.report_dir).expanduser().resolve() / report_folder
                command.extend(["--report-dir", str(target_report_dir)])
            result = subprocess.run(command, check=False)
            if result.returncode != 0:
                failure_count += 1
        print("\n" + "=" * 88, flush=True)
        if failure_count:
            print(f" COMPLETE SUITE FINISHED — {failure_count} SECTION(S) WITH FAILURES ".center(88, "="), flush=True)
        else:
            print(" COMPLETE SUITE FINISHED — ALL SECTIONS PASSED ".center(88, "="), flush=True)
        print("=" * 88, flush=True)
        return 1 if failure_count else 0

    base_url = _normalise_url(args.url)
    run_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    report_dir = Path(args.report_dir).expanduser().resolve() if args.report_dir else (REPORTS_DIR / run_id).resolve()
    report_dir.mkdir(parents=True, exist_ok=True)
    results_file = report_dir / "results.json"
    specs_file = report_dir / "case_specs.json"
    screenshot_dir = report_dir / "screenshots"
    results_file.write_text("[]", encoding="utf-8")

    if args.section == "main":
        section_title = "Section 01 — Main Page"
        scope_description = (
            "Homepage navigation, cart entry and return, product cards, collection links, "
            "footer links, policies, FAQ, and every currency option discovered in the currency selector."
        )
        test_file = Path(__file__).resolve().parent / "tests" / "test_01_main_page.py"
        print("\n" + "=" * 88, flush=True)
        print(f" {section_title.upper()} ".center(88, "="), flush=True)
        print("=" * 88, flush=True)
        print(f"E-commerce UI Automation — {section_title}")
        print(f"Store: {base_url}")
        print(f"Scope: {scope_description}")
        print("Discovering the homepage and available currency options...", flush=True)
        specs, discovery = discover(base_url, args.headless, max(0, args.slowmo), report_dir)
    else:
        section = SECTION_CONFIGS[args.section]
        section_title = section["section_title"]
        scope_description = section["scope"]
        test_file = Path(__file__).resolve().parent / "tests" / section["test_file"]
        print("\n" + "=" * 88, flush=True)
        print(f" {section_title.upper()} ".center(88, "="), flush=True)
        print("=" * 88, flush=True)
        print(f"E-commerce UI Automation — {section_title}")
        print(f"Store: {base_url}")
        print(f"Scope: {scope_description}")
        print("Discovering collection products and selectable size options...", flush=True)
        specs, discovery = discover_collection_section(
            base_url, args.section, args.headless, max(0, args.slowmo), report_dir
        )
    specs_file.write_text(json.dumps(specs, ensure_ascii=False, indent=2), encoding="utf-8")
    os.environ.update({
        "BASE_URL": base_url,
        "E2E_CASE_SPECS": str(specs_file),
        "E2E_RESULTS_FILE": str(results_file),
        "E2E_SCREENSHOT_DIR": str(screenshot_dir),
        "E2E_REPORT_DIR": str(report_dir),
        "E2E_HEADLESS": "1" if args.headless else "0",
        "E2E_SLOWMO": str(max(0, args.slowmo)),
    })

    if args.section == "main":
        print(f"Discovered {discovery.get('links_discovered', 0)} visible homepage links.")
        print(f"Currency options: {len([case for case in specs if case.get('kind') == 'currency_option'])} detected.")
    else:
        duplicate_count = len(discovery.get("duplicate_product_listings", []))
        card_count = discovery.get("product_cards_found", discovery.get("products_discovered", 0))
        print(f"Collection product cards found: {card_count} unique URL(s).")
        print(f"Unique products to open: {discovery.get('products_discovered', 0)}.")
        if duplicate_count:
            print(
                f"Potential repeated titles: {duplicate_count} (reported separately; "
                "all distinct product URLs remain included in variant tests)."
            )
        print("Each product is opened once; only actual size/capacity options are clicked.")
    if args.section == "main":
        print(f"Running {len(specs)} independent checks...\n", flush=True)
    else:
        print(f"Running {len(specs)} pytest cases; product cases check all sizes in one visit...\n", flush=True)

    pytest_args = ["-q", "--tb=no", "--disable-warnings", str(test_file)]
    exit_code = int(pytest.main(pytest_args))

    try:
        results = json.loads(results_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        results = []
    report_path = build_html_report(
        report_dir, base_url, discovery, results, exit_code,
        section_title=section_title, scope_description=scope_description,
    )
    counts = {key: sum(1 for row in results if row.get("status") == key) for key in ("PASS", "FAIL", "SKIP")}
    total = sum(counts.values())

    print(f"\n=== {section_title.upper()} SUMMARY ===")
    print(f"Pytest cases: {len(specs)}")
    print(f"Individual result rows recorded: {total}")
    print(f"PASS: {counts['PASS']} | FAIL: {counts['FAIL']} | SKIP: {counts['SKIP']}")
    print(f"HTML report: {report_path}")
    print(f"JSON report: {report_dir / 'report.json'}")
    if discovery.get("homepage_screenshot"):
        print(f"Homepage screenshot: {report_dir / discovery['homepage_screenshot']}")
    elif discovery.get("section_screenshot"):
        print(f"Collection screenshot: {report_dir / discovery['section_screenshot']}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
