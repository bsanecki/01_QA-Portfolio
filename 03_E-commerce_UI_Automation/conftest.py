"""Pytest fixtures and compact per-test console progress output."""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright

from config import BASE_URL, VIEWPORT
from ecomqa.browser import launch_chromium

_TOTAL = 0
_COMPLETED = 0
_PRINTED: set[str] = set()
_CONFIG = None


@pytest.fixture(scope="session")
def base_url() -> str:
    return os.getenv("BASE_URL", BASE_URL)


@pytest.fixture(scope="session")
def browser():
    headless = os.getenv("E2E_HEADLESS", "0") == "1"
    slow_mo = int(os.getenv("E2E_SLOWMO", "50"))
    with sync_playwright() as playwright:
        instance = launch_chromium(playwright, headless=headless, slow_mo=slow_mo)
        yield instance
        instance.close()


@pytest.fixture
def browser_context(browser):
    context = browser.new_context(viewport=VIEWPORT, accept_downloads=True, reduced_motion="reduce")
    yield context
    context.close()


def pytest_generate_tests(metafunc):
    if "case_spec" not in metafunc.fixturenames:
        return
    specs_path = os.getenv("E2E_CASE_SPECS")
    specs = []
    if specs_path and Path(specs_path).exists():
        try:
            specs = json.loads(Path(specs_path).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            specs = []
    if not specs:
        specs = [{
            "id": "setup-error", "kind": "setup_error", "label": "Test case discovery",
            "discovered": False, "discoveryNote": "No test case list was generated. Run python run_tests.py.",
        }]
    params = []
    for spec in specs:
        suffix = re.sub(r"[^a-zA-Z0-9_-]+", "-", spec.get("label", "check")).strip("-")[:55] or "check"
        params.append(pytest.param(spec, id=f"{spec.get('id', 'case')}-{suffix}"))
    metafunc.parametrize("case_spec", params)


def pytest_configure(config):
    global _CONFIG
    _CONFIG = config


def pytest_collection_finish(session):
    global _TOTAL, _COMPLETED
    _TOTAL = len(session.items)
    _COMPLETED = 0
    _PRINTED.clear()


def pytest_report_teststatus(report, config):
    # Keep pytest's real test accounting, but suppress phase-level setup/teardown counts.
    if report.when == "call":
        if report.passed:
            return "passed", "", "PASSED"
        if report.skipped:
            return "skipped", "", "SKIPPED"
        if report.failed:
            return "failed", "", "FAILED"
    elif report.when == "setup" and (report.failed or report.skipped):
        if report.skipped:
            return "skipped", "", "SKIPPED"
        return "failed", "", "FAILED"
    return None


def _case_for_nodeid(nodeid: str) -> dict | None:
    specs_path = os.getenv("E2E_CASE_SPECS")
    if not specs_path or not Path(specs_path).exists():
        return None
    try:
        specs = json.loads(Path(specs_path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    param_id = nodeid.rsplit("[", 1)[-1].rstrip("]") if "[" in nodeid else ""
    matches = [spec for spec in specs if param_id.startswith(str(spec.get("id", "")) + "-") or param_id == str(spec.get("id", ""))]
    return max(matches, key=lambda spec: len(str(spec.get("id", "")))) if matches else None


def _record_hook_failure(report) -> None:
    # Browser launch/fixture errors happen before the test body can write a normal result.
    results_path = os.getenv("E2E_RESULTS_FILE")
    spec = _case_for_nodeid(report.nodeid)
    if not results_path or not spec:
        return
    try:
        from ecomqa.reporting import write_result
        short_error = "\n".join(str(report.longrepr).splitlines()[:3])[:700]
        write_result(results_path, {
            "id": spec.get("id", "unknown"),
            "kind": spec.get("kind", "unknown"),
            "label": spec.get("label", "Unnamed check"),
            "status": "FAIL",
            "details": f"Test setup/teardown failed before the check could finish: {short_error}",
            "duration_ms": 0,
            "screenshot": None,
        })
    except Exception:
        pass


def pytest_runtest_logreport(report):
    global _COMPLETED
    if report.when == "call":
        key = report.nodeid
    elif report.when == "setup" and report.outcome in ("failed", "skipped"):
        key = report.nodeid
        if report.failed:
            _record_hook_failure(report)
    elif report.when == "teardown" and report.outcome == "failed":
        key = report.nodeid
        _record_hook_failure(report)
    else:
        return
    if key in _PRINTED:
        return
    _PRINTED.add(key)
    _COMPLETED += 1
    total = max(_TOTAL, 1)
    percent = min(100, round((_COMPLETED / total) * 100))
    if report.outcome == "passed":
        marker, status = ".", "PASS"
    elif report.outcome == "skipped":
        marker, status = "s", "SKIP"
    else:
        marker, status = "F", "FAIL"
    test_id = report.nodeid.rsplit("[", 1)[-1].rstrip("]") if "[" in report.nodeid else report.nodeid.split("::")[-1]
    terminal = _CONFIG.pluginmanager.get_plugin("terminalreporter") if _CONFIG is not None else None
    if terminal:
        terminal.write_line(f"[{percent:3d}%] {marker} {status:<4} | {test_id}")
