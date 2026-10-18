#!/usr/bin/env python3
"""Run storefront test sections sequentially and create one combined suite report."""
from __future__ import annotations

import argparse
import json
import os
import shutil
import hashlib
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
from ecomqa.reporting import build_html_report, normalize_report_text
from ecomqa.collection_testing import SECTION_CONFIGS, discover_collection_section
from ecomqa.cart_testing import build_cart_specs


def parse_args():
    parser = argparse.ArgumentParser(description="E-commerce UI Automation - sectioned test runner")
    parser.add_argument("--headless", action="store_true", help="Run Chromium without a visible window")
    parser.add_argument("--slowmo", type=int, default=50, help="Slow down browser actions in milliseconds (default: 50)")
    parser.add_argument("--url", default=BASE_URL, help="Homepage URL to test")
    parser.add_argument(
        "--section",
        choices=("all", "main", "tshirts", "mugs", "cart"),
        default="all",
        help="Run all sections (default), or only main, tshirts, mugs, or cart.",
    )
    parser.add_argument("--report-dir", default=None, help="Custom report directory (suite root when running all sections)")
    parser.add_argument("--_suppress-report", action="store_true", help=argparse.SUPPRESS)
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



def _copy_report_artifact(
    path_value: str | Path | None,
    section_dir: Path,
    suite_dir: Path,
    report_folder: str,
    artifact_kind: str,
) -> tuple[str | None, str | None]:
    """Copy screenshot evidence into stable paths relative to the combined report."""
    if not path_value:
        return None, None

    raw_path = Path(str(path_value)).expanduser()
    candidates = [raw_path] if raw_path.is_absolute() else [
        section_dir / raw_path,
        suite_dir / raw_path,
        Path.cwd() / raw_path,
    ]
    source = None
    for candidate in candidates:
        try:
            resolved = candidate.resolve()
        except OSError:
            continue
        if resolved.is_file():
            source = resolved
            break

    if source is None:
        return None, f"Original evidence file was not found: {path_value}"

    # Put evidence alongside the single combined report so links stay valid and portable.
    target_dir = suite_dir / "evidence" / report_folder / artifact_kind
    target_dir.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha1(str(source).encode("utf-8")).hexdigest()[:8]
    target_name = f"{source.stem}-{digest}{source.suffix or '.png'}"
    target = target_dir / target_name
    try:
        if source != target.resolve():
            shutil.copy2(source, target)
    except OSError as exc:
        return None, f"Could not copy evidence file '{source}': {type(exc).__name__}: {exc}"

    return target.relative_to(suite_dir).as_posix(), None


def _prepare_single_section_report_data(
    report_dir: Path,
    section_key: str,
    discovery: dict,
    results: list[dict],
) -> tuple[dict, list[dict]]:
    """Copy only report-relevant screenshots into stable evidence links and sanitize values."""
    folder_names = {
        "main": "section-01-main",
        "tshirts": "section-02-tshirts",
        "mugs": "section-03-mugs",
        "cart": "section-04-cart",
    }
    report_folder = folder_names.get(section_key, f"section-{section_key}")
    cleaned_discovery = normalize_report_text(dict(discovery or {}))
    cleaned_results: list[dict] = []

    preview_key = "section_screenshot" if cleaned_discovery.get("section_screenshot") else "homepage_screenshot"
    preview_source = cleaned_discovery.get(preview_key)
    preview_path, preview_error = _copy_report_artifact(
        preview_source, report_dir, report_dir, report_folder, "previews"
    ) if preview_source else (None, None)
    if preview_source:
        cleaned_discovery[preview_key] = preview_path
    if preview_error:
        cleaned_discovery["preview_screenshot_error"] = preview_error

    for original in results:
        row = normalize_report_text(dict(original))
        screenshot_source = row.get("screenshot")
        if screenshot_source:
            screenshot_path, screenshot_error = _copy_report_artifact(
                screenshot_source, report_dir, report_dir, report_folder, "results"
            )
            row["screenshot"] = screenshot_path
            if screenshot_error:
                row["screenshot_error"] = screenshot_error
            else:
                row.pop("screenshot_error", None)
        cleaned_results.append(row)

    # Keep a useful reference when a failing check did not produce its own screenshot.
    if preview_path:
        for row in cleaned_results:
            if row.get("status") == "FAIL" and not row.get("screenshot"):
                previous_error = row.pop("screenshot_error", None)
                row["screenshot"] = preview_path
                row["screenshot_note"] = (
                    f"Section preview used because the individual screenshot was unavailable: {previous_error}"
                    if previous_error else
                    "Section preview used because this check did not produce an individual screenshot."
                )
    return cleaned_discovery, cleaned_results


def _cleanup_temporary_report_files(report_dir: Path, *, remove_sections: bool = False) -> None:
    """Leave only report.html, report.json and the evidence folder in the final report directory."""
    for filename in ("results.json", "case_specs.json", "section_metadata.json", "homepage-preview.png", "collection-preview.png"):
        try:
            (report_dir / filename).unlink(missing_ok=True)
        except OSError:
            pass
    for dirname in ("screenshots",):
        shutil.rmtree(report_dir / dirname, ignore_errors=True)
    if remove_sections:
        shutil.rmtree(report_dir / "sections", ignore_errors=True)


def main() -> int:
    args = parse_args()

    # The complete run keeps section artifacts separated, but creates only ONE shared report.
    if args.section == "all":
        script = str(Path(__file__).resolve())
        sections = (
            ("main", "Section 01 - Main Page", "section-01-main"),
            ("tshirts", "Section 02 - T-shirt Collection", "section-02-tshirts"),
            ("mugs", "Section 03 - Mug Collection", "section-03-mugs"),
            ("cart", "Section 04 - Cart", "section-04-cart"),
        )
        run_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        suite_dir = Path(args.report_dir).expanduser().resolve() if args.report_dir else (REPORTS_DIR / run_id).resolve()
        suite_dir.mkdir(parents=True, exist_ok=True)
        sections_root = suite_dir / "sections"

        print("\n" + "=" * 88, flush=True)
        print(" E-COMMERCE UI AUTOMATION - COMPLETE TEST SUITE ".center(88, "="), flush=True)
        print("One combined HTML/JSON report will be generated after all sections finish.", flush=True)
        print("=" * 88, flush=True)

        section_exit_codes: dict[str, int] = {}
        for section_key, section_title, report_folder in sections:
            section_dir = sections_root / report_folder
            command = [
                sys.executable, script,
                "--section", section_key,
                "--url", args.url,
                "--slowmo", str(max(0, args.slowmo)),
                "--report-dir", str(section_dir),
                "--_suppress-report",
            ]
            if args.headless:
                command.append("--headless")
            child = subprocess.run(command, check=False)
            section_exit_codes[section_key] = int(child.returncode)

        combined_results: list[dict] = []
        section_summaries: list[dict] = []
        section_discoveries: list[dict] = []
        summary_sections = []

        for section_key, section_title, report_folder in sections:
            section_dir = sections_root / report_folder
            results_file = section_dir / "results.json"
            metadata_file = section_dir / "section_metadata.json"
            try:
                section_results = json.loads(results_file.read_text(encoding="utf-8"))
                if not isinstance(section_results, list):
                    section_results = []
            except (OSError, json.JSONDecodeError):
                section_results = []

            try:
                metadata = json.loads(metadata_file.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                metadata = {
                    "section_key": section_key,
                    "section_title": section_title,
                    "scope_description": "Section metadata was not available.",
                    "discovery": {},
                    "pytest_cases": 0,
                }

            exit_code = section_exit_codes.get(section_key, 1)
            if exit_code != 0 and not any(row.get("status") == "FAIL" for row in section_results):
                section_results.append({
                    "id": f"section-execution-{section_key}",
                    "kind": "section_execution",
                    "label": "Section execution failed",
                    "status": "FAIL",
                    "details": f"The section process exited with code {exit_code}, but no individual FAIL result was recorded. Check the terminal output for the underlying pytest or setup error.",
                    "duration_ms": 0,
                    "screenshot": None,
                })

            # Copy screenshots into a stable evidence folder next to the combined report.
            section_result_start = len(combined_results)
            for original in section_results:
                row = normalize_report_text(dict(original))
                row["section"] = section_title
                screenshot = row.get("screenshot")
                if screenshot:
                    copied_path, screenshot_error = _copy_report_artifact(
                        screenshot, section_dir, suite_dir, report_folder, "results"
                    )
                    row["screenshot"] = copied_path
                    if screenshot_error:
                        row["screenshot_error"] = screenshot_error
                    else:
                        row.pop("screenshot_error", None)
                combined_results.append(row)

            counts = {key: sum(1 for row in section_results if row.get("status") == key) for key in ("PASS", "FAIL", "SKIP")}
            total_rows = sum(counts.values())
            section_status = "FAIL" if exit_code != 0 or counts["FAIL"] else ("PASS" if total_rows else "UNKNOWN")
            discovery_data = normalize_report_text(metadata.get("discovery", {}) if isinstance(metadata.get("discovery"), dict) else {})
            raw_preview_screenshot = discovery_data.get("section_screenshot") or discovery_data.get("homepage_screenshot")
            preview_screenshot, preview_screenshot_error = _copy_report_artifact(
                raw_preview_screenshot, section_dir, suite_dir, report_folder, "previews"
            ) if raw_preview_screenshot else (None, None)
            section_summaries.append({
                "section_key": section_key,
                "section_title": section_title,
                "status": section_status,
                "pytest_cases": metadata.get("pytest_cases", 0),
                "result_rows": total_rows,
                "counts": counts,
                "pytest_exit_code": exit_code,
                "preview_screenshot": preview_screenshot,
                "preview_screenshot_error": preview_screenshot_error,
            })
            discovery_copy = dict(discovery_data)
            if discovery_copy.get("homepage_screenshot"):
                discovery_copy["homepage_screenshot"] = preview_screenshot
            if discovery_copy.get("section_screenshot"):
                discovery_copy["section_screenshot"] = preview_screenshot
            if preview_screenshot_error:
                discovery_copy["preview_screenshot_error"] = preview_screenshot_error

            # Discovery-style failures may not create a per-check screenshot. Link the
            # section preview as fallback evidence rather than leaving an empty cell.
            if preview_screenshot:
                for row in combined_results[section_result_start:]:
                    if row.get("status") == "FAIL" and not row.get("screenshot"):
                        original_error = row.pop("screenshot_error", None)
                        row["screenshot"] = preview_screenshot
                        row["screenshot_note"] = (
                            f"Section preview used because the individual screenshot was unavailable: {original_error}"
                            if original_error else
                            "Section preview used because this check did not produce an individual screenshot."
                        )
            section_discoveries.append({"section_key": section_key, "section_title": section_title, "discovery": discovery_copy})
            summary_sections.append(str(metadata.get("scope_description", section_title)))

        aggregate_exit_code = 1 if any(item["pytest_exit_code"] != 0 or item["status"] == "FAIL" for item in section_summaries) else 0
        aggregate_discovery = {
            "section_summaries": section_summaries,
            "sections": section_discoveries,
        }
        main_preview = next((item["preview_screenshot"] for item in section_summaries if item["section_key"] == "main"), None)
        if main_preview:
            aggregate_discovery["homepage_screenshot"] = main_preview

        combined_scope = "\n\n".join(
            f"{section_title}: {metadata_scope}"
            for (_, section_title, _), metadata_scope in zip(sections, summary_sections)
        )
        report_path = build_html_report(
            suite_dir,
            _normalise_url(args.url),
            aggregate_discovery,
            combined_results,
            aggregate_exit_code,
            section_title="Complete Test Suite - All Sections",
            scope_description=combined_scope,
        )
        # Child-section artifacts were only needed while assembling the final report.
        # Keep the unified HTML/JSON reports and unique evidence screenshots only.
        _cleanup_temporary_report_files(suite_dir, remove_sections=True)
        try:
            total_counts = {key: sum(1 for row in combined_results if row.get("status") == key) for key in ("PASS", "FAIL", "SKIP")}
        except Exception:
            total_counts = {"PASS": 0, "FAIL": 0, "SKIP": 0}

        print("\n" + "=" * 88, flush=True)
        print(" COMPLETE SUITE SUMMARY ".center(88, "="), flush=True)
        for summary in section_summaries:
            counts = summary["counts"]
            print(
                f"{summary['section_title']}: {summary['status']} - "
                f"PASS {counts['PASS']} | FAIL {counts['FAIL']} | SKIP {counts['SKIP']}",
                flush=True,
            )
        print("-" * 88, flush=True)
        print(f"TOTAL: PASS {total_counts['PASS']} | FAIL {total_counts['FAIL']} | SKIP {total_counts['SKIP']}", flush=True)
        print(f"Combined HTML report: {report_path}", flush=True)
        print(f"Combined JSON report: {suite_dir / 'report.json'}", flush=True)
        if aggregate_exit_code:
            print(" COMPLETE SUITE FINISHED - FAILURES DETECTED ".center(88, "="), flush=True)
        else:
            print(" COMPLETE SUITE FINISHED - ALL CHECKS PASSED ".center(88, "="), flush=True)
        print("=" * 88, flush=True)
        return aggregate_exit_code

    base_url = _normalise_url(args.url)
    run_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    report_dir = Path(args.report_dir).expanduser().resolve() if args.report_dir else (REPORTS_DIR / run_id).resolve()
    report_dir.mkdir(parents=True, exist_ok=True)
    results_file = report_dir / "results.json"
    specs_file = report_dir / "case_specs.json"
    screenshot_dir = report_dir / "screenshots"
    results_file.write_text("[]", encoding="utf-8")

    if args.section == "main":
        section_title = "Section 01 - Main Page"
        scope_description = (
            "Homepage navigation, cart entry and return, product cards, collection links, "
            "footer links, policies, FAQ, and every currency option discovered in the currency selector."
        )
        test_file = Path(__file__).resolve().parent / "tests" / "test_01_main_page.py"
        print("\n" + "=" * 88, flush=True)
        print(f" {section_title.upper()} ".center(88, "="), flush=True)
        print("=" * 88, flush=True)
        print(f"E-commerce UI Automation - {section_title}")
        print(f"Store: {base_url}")
        print(f"Scope: {scope_description}")
        print("Discovering the homepage and available currency options...", flush=True)
        specs, discovery = discover(base_url, args.headless, max(0, args.slowmo), report_dir)
    elif args.section == "cart":
        section_title = "Section 04 - Cart"
        scope_description = (
            "Add three fixed test products in an isolated browser context, verify cart contents and subtotal, "
            "increase quantity from one to two, verify subtotal recalculation, remove a product, verify the "
            "subtotal decrease, open checkout only to confirm the next step loads, then empty the test cart. "
            "No order or payment is submitted."
        )
        test_file = Path(__file__).resolve().parent / "tests" / "test_04_cart.py"
        print("\n" + "=" * 88, flush=True)
        print(f" {section_title.upper()} ".center(88, "="), flush=True)
        print("=" * 88, flush=True)
        print(f"E-commerce UI Automation - {section_title}")
        print(f"Store: {base_url}")
        print(f"Scope: {scope_description}")
        print("Preparing the fixed cart test products...", flush=True)
        specs, discovery = build_cart_specs(base_url)
    else:
        section = SECTION_CONFIGS[args.section]
        section_title = section["section_title"]
        scope_description = section["scope"]
        test_file = Path(__file__).resolve().parent / "tests" / section["test_file"]
        print("\n" + "=" * 88, flush=True)
        print(f" {section_title.upper()} ".center(88, "="), flush=True)
        print("=" * 88, flush=True)
        print(f"E-commerce UI Automation - {section_title}")
        print(f"Store: {base_url}")
        print(f"Scope: {scope_description}")
        print("Discovering collection products and selectable size options...", flush=True)
        specs, discovery = discover_collection_section(
            base_url, args.section, args.headless, max(0, args.slowmo), report_dir
        )
    specs_file.write_text(json.dumps(normalize_report_text(specs), ensure_ascii=False, indent=2), encoding="utf-8")
    os.environ.update({
        "BASE_URL": base_url,
        "E2E_CASE_SPECS": str(specs_file),
        "E2E_RESULTS_FILE": str(results_file),
        "E2E_SCREENSHOT_DIR": str(screenshot_dir),
        "E2E_REPORT_DIR": str(report_dir),
        "E2E_HEADLESS": "1" if args.headless else "0",
        "E2E_SLOWMO": str(max(0, args.slowmo)),
        "E2E_CART_LIVE_LOG": "1" if args.section == "cart" else "0",
    })

    if args.section == "main":
        print(f"Discovered {discovery.get('links_discovered', 0)} visible homepage links.")
        print(f"Currency options: {len([case for case in specs if case.get('kind') == 'currency_option'])} detected.")
        print(f"Running {len(specs)} independent checks...\n", flush=True)
    elif args.section == "cart":
        print(f"Fixed cart products: {len(discovery.get('products', []))}.")
        for product in discovery.get("products", []):
            print(f"  - {product['label']}: {product['url']}")
        print("Running one stateful cart workflow; every action receives its own result...\n", flush=True)
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
        print(f"Running {len(specs)} pytest cases; product cases check all sizes in one visit...\n", flush=True)

    pytest_args = ["-q", "--tb=no", "--disable-warnings"]
    # Let the cart workflow stream its numbered stages and per-action results live.
    if args.section == "cart":
        pytest_args.append("-s")
    pytest_args.append(str(test_file))
    exit_code = int(pytest.main(pytest_args))

    try:
        results = json.loads(results_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        results = []
    metadata = {
        "section_key": args.section,
        "section_title": section_title,
        "scope_description": scope_description,
        "discovery": discovery,
        "pytest_cases": len(specs),
        "pytest_exit_code": exit_code,
    }
    metadata = normalize_report_text(metadata)
    (report_dir / "section_metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    counts = {key: sum(1 for row in results if row.get("status") == key) for key in ("PASS", "FAIL", "SKIP")}
    total = sum(counts.values())

    report_path = None
    if not args._suppress_report:
        report_discovery, report_results = _prepare_single_section_report_data(
            report_dir, args.section, discovery, results
        )
        report_path = build_html_report(
            report_dir, base_url, report_discovery, report_results, exit_code,
            section_title=section_title, scope_description=scope_description,
        )
        _cleanup_temporary_report_files(report_dir)

    print(f"\n=== {section_title.upper()} SUMMARY ===")
    print(f"Pytest cases: {len(specs)}")
    print(f"Individual result rows recorded: {total}")
    print(f"PASS: {counts['PASS']} | FAIL: {counts['FAIL']} | SKIP: {counts['SKIP']}")
    if report_path:
        print(f"HTML report: {report_path}")
        print(f"JSON report: {report_dir / 'report.json'}")
    else:
        print("Section results saved for the combined suite report.")
    if report_path and (report_dir / "evidence").exists():
        print(f"Evidence: {report_dir / 'evidence'}")
    elif args._suppress_report and discovery.get("homepage_screenshot"):
        print(f"Homepage screenshot: {report_dir / discovery['homepage_screenshot']}")
    elif args._suppress_report and discovery.get("section_screenshot"):
        print(f"Collection screenshot: {report_dir / discovery['section_screenshot']}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
