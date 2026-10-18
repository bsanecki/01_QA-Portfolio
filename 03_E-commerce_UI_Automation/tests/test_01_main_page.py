"""Section 01: independent checks for the PandaPocket homepage."""
from __future__ import annotations

import os
import re
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import pytest
from playwright.sync_api import Error as PlaywrightError

from config import ACTION_TIMEOUT_MS, DISCOVERY_WAIT_MS, NAVIGATION_TIMEOUT_MS, POST_CLICK_WAIT_MS
from ecomqa.discovery import CURRENT_CURRENCY_SCRIPT, CURRENCY_TRIGGER_SCRIPT, FIND_TARGET_SCRIPT
from ecomqa.reporting import write_result

RESULTS_FILE = Path(os.environ.get("E2E_RESULTS_FILE", "reports/results.json"))
SCREENSHOT_DIR = Path(os.environ.get("E2E_SCREENSHOT_DIR", "reports/screenshots"))
REPORT_DIR = Path(os.environ.get("E2E_REPORT_DIR", "reports"))


def _normal_path(value: str) -> str:
    return urlsplit(value).path.rstrip("/") or "/"


def _visible_snapshot(page) -> dict[str, Any]:
    return page.evaluate(r"""() => {
      const norm = v => String(v || '').replace(/\s+/g, ' ').trim();
      const visible = el => { const s=getComputedStyle(el), r=el.getBoundingClientRect(); return s.display!=='none' && s.visibility!=='hidden' && Number(s.opacity)!==0 && r.width>0 && r.height>0; };
      const prices = Array.from(document.querySelectorAll('[class*="price" i], [data-price], [itemprop="price"]'))
        .filter(visible).map(el => norm(el.innerText || el.getAttribute('content'))).filter(Boolean).slice(0,24);
      const text = norm(document.body ? document.body.innerText : '').slice(0, 1200);
      return {title: document.title, bodyText: text, prices};
    }""")


def _save_screenshot(page, spec: dict[str, Any]) -> str | None:
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    filename = re.sub(r"[^a-zA-Z0-9_-]+", "-", spec.get("id", "failed-check")).strip("-") or "failed-check"
    path = SCREENSHOT_DIR / f"{filename}.png"
    try:
        page.screenshot(path=str(path), full_page=False, timeout=5000)
        return str(path.resolve().relative_to(REPORT_DIR.resolve()))
    except Exception:
        return None


def _record(spec: dict[str, Any], status: str, details: str, started: float, screenshot: str | None = None, request=None) -> None:
    row = {
        "id": spec.get("id", "unknown-check"),
        "kind": spec.get("kind", "unknown"),
        "label": spec.get("label", "Unnamed check"),
        "status": status,
        "details": details,
        "duration_ms": round((time.monotonic() - started) * 1000),
        "screenshot": screenshot,
    }
    write_result(RESULTS_FILE, row)
    if request is not None:
        request.node.user_properties.append(("case_status", status))
        request.node.user_properties.append(("case_details", details))


def _open_home(page, base_url: str):
    page.set_default_timeout(ACTION_TIMEOUT_MS)
    page.set_default_navigation_timeout(NAVIGATION_TIMEOUT_MS)
    response = page.goto(base_url, wait_until="domcontentloaded", timeout=NAVIGATION_TIMEOUT_MS)
    page.wait_for_timeout(DISCOVERY_WAIT_MS)
    return response


def _find_target(page, spec: dict[str, Any]) -> dict[str, Any]:
    return page.evaluate(FIND_TARGET_SCRIPT, spec)


def _target_locator(page, spec: dict[str, Any]):
    return page.locator(f'[data-qa-target="{spec["id"]}"]')


def _dismiss_cookie_notice(page) -> str | None:
    """Dismiss a cookie notice in the isolated context so it cannot block the target control."""
    patterns = [
        re.compile(r"reject\s+all|only\s+necessary|essential\s+only|reject\s+optional|necessary\s+only", re.I),
        re.compile(r"accept\s+all|accept\s+cookies|allow\s+all|agree\s+and\s+continue", re.I),
    ]
    for pattern in patterns:
        try:
            buttons = page.get_by_role("button", name=pattern)
            for index in range(min(buttons.count(), 6)):
                button = buttons.nth(index)
                try:
                    if button.is_visible() and button.is_enabled():
                        label = (button.inner_text(timeout=400) or button.get_attribute("aria-label") or "Reject optional cookies").strip()
                        button.click(timeout=1200)
                        page.wait_for_timeout(150)
                        return f"Dismissed cookie notice using '{label}'."
                except PlaywrightError:
                    continue
        except PlaywrightError:
            continue
    return None


def _collect_navigation(page, context):
    responses: list[dict[str, Any]] = []
    popups: list[Any] = []

    def listen_response(response, source_page):
        try:
            if response.request.is_navigation_request() and response.frame == source_page.main_frame:
                responses.append({"url": response.url, "status": response.status})
        except PlaywrightError:
            pass

    page.on("response", lambda response: listen_response(response, page))

    def on_page(new_page):
        if new_page is page:
            return
        popups.append(new_page)
        new_page.on("response", lambda response: listen_response(response, new_page))

    context.on("page", on_page)
    return responses, popups


def _latest_status(responses: list[dict[str, Any]], url: str) -> int | None:
    target_path = _normal_path(url)
    for response in reversed(responses):
        if _normal_path(response["url"]) == target_path:
            return int(response["status"])
    return None


def _click_target(page, context, spec: dict[str, Any]):
    found = _find_target(page, spec)
    if not found.get("found"):
        raise AssertionError("Expected control was not found on the freshly opened homepage.")
    locator = _target_locator(page, spec)
    if locator.count() != 1:
        raise AssertionError(f"Target locator is not unique (count={locator.count()}).")
    if not locator.is_visible():
        raise AssertionError("Target exists in the DOM but is not visible.")
    if not locator.is_enabled():
        raise AssertionError("Target is disabled and cannot be clicked.")
    responses, popups = _collect_navigation(page, context)
    # Capture the current URL before clicking; this is used to verify that
    # navigation actually happened and to distinguish real site failures.
    before_url = page.url
    click_error = None
    try:
        locator.click(timeout=ACTION_TIMEOUT_MS)
    except PlaywrightError as exc:
        click_error = f"{type(exc).__name__}: {str(exc).splitlines()[0][:220]}"
    page.wait_for_timeout(POST_CLICK_WAIT_MS)
    target_page = popups[-1] if popups else page
    try:
        target_page.wait_for_load_state("domcontentloaded", timeout=2000)
    except PlaywrightError:
        pass
    return {
        "found": found,
        "locator": locator,
        "before_url": before_url,
        "after_url": target_page.url,
        "target_page": target_page,
        "popups": popups,
        "responses": responses,
        "status": _latest_status(responses, target_page.url),
        "click_error": click_error,
    }


def _return_home(page, base_url: str) -> tuple[bool, str]:
    try:
        response = page.go_back(wait_until="domcontentloaded", timeout=NAVIGATION_TIMEOUT_MS)
        page.wait_for_timeout(350)
        returned_path = _normal_path(page.url)
        home_path = _normal_path(base_url)
        status = response.status if response is not None else None
        ok = returned_path == home_path and (status is None or status < 400)
        return ok, f"Returned URL={page.url}; HTTP {status if status is not None else 'not exposed by browser history'}."
    except Exception as exc:
        return False, f"Could not return to the homepage: {type(exc).__name__}: {str(exc).splitlines()[0][:180]}"


def _fail(page, spec, request, started, details):
    screenshot = _save_screenshot(page, spec)
    _record(spec, "FAIL", details, started, screenshot, request)
    pytest.fail(details, pytrace=False)


def _test_navigation_case(page, context, spec, base_url: str, request, started) -> None:
    if not spec.get("discovered"):
        _fail(page, spec, request, started, spec.get("discoveryNote", "Expected homepage control was not discovered."))

    _dismiss_cookie_notice(page)
    try:
        action = _click_target(page, context, spec)
    except Exception as exc:
        _fail(page, spec, request, started, f"Could not click the expected control: {type(exc).__name__}: {str(exc).splitlines()[0][:240]}")

    target_page = action["target_page"]
    after_url = action["after_url"]
    status = action["status"]
    before_url = action["before_url"]
    kind = spec["kind"]
    expected_path = spec.get("hrefPath", "")
    landed_path = _normal_path(after_url)
    home_path = _normal_path(base_url)
    navigated = after_url != before_url or bool(action["popups"])

    if action["click_error"] and not navigated:
        _fail(page, spec, request, started, f"Click failed and no navigation occurred: {action['click_error']}")
    if kind == "home_navigation":
        if landed_path != home_path:
            _fail(target_page, spec, request, started, f"Home navigation did not end on the homepage. Landed on {after_url}.")
        if status is not None and status >= 400:
            _fail(target_page, spec, request, started, f"Home navigation returned HTTP {status}: {after_url}")
        _record(spec, "PASS", f"Home link was clickable and the browser remained on the homepage ({after_url}).", started, request=request)
        return

    if not navigated:
        _fail(target_page, spec, request, started, f"Click completed without navigating or opening a new tab. URL remained {after_url}.")

    if status is not None and status >= 400:
        _fail(target_page, spec, request, started, f"Click navigated to an HTTP error page: HTTP {status} — {after_url}")

    if expected_path and landed_path != _normal_path(expected_path):
        if not any(_normal_path(response["url"]) == _normal_path(expected_path) and response["status"] < 400 for response in action["responses"]):
            _fail(target_page, spec, request, started, f"Unexpected destination. Expected {expected_path}; landed on {after_url}.")

    if kind == "cart_round_trip":
        if not re.search(r"/(cart|basket)/?$", urlsplit(after_url).path, re.I):
            _fail(target_page, spec, request, started, f"Cart control did not open the cart. Landed on {after_url}.")
        returned, return_details = _return_home(target_page, base_url)
        if not returned:
            _fail(target_page, spec, request, started, f"Cart opened, but returning to the homepage failed. {return_details}")
        _record(spec, "PASS", f"Cart opened successfully ({after_url}) and returning to the homepage worked. {return_details}", started, request=request)
        return

    if kind == "product":
        if "/products/" not in urlsplit(after_url).path.lower():
            _fail(target_page, spec, request, started, f"Product card did not open a product detail page. Landed on {after_url}.")
        if action["popups"]:
            for popup in action["popups"]:
                try:
                    popup.close()
                except PlaywrightError:
                    pass
            _record(spec, "PASS", f"Product opened in a new tab ({after_url}); closing the tab returned control to the homepage.", started, request=request)
            return
        returned, return_details = _return_home(target_page, base_url)
        if not returned:
            _fail(target_page, spec, request, started, f"Product page opened, but returning to the homepage failed. {return_details}")
        _record(spec, "PASS", f"Product opened successfully ({after_url}) and returning to the homepage worked. {return_details}", started, request=request)
        return

    _record(spec, "PASS", f"Link opened successfully: {after_url}" + (f" (HTTP {status})" if status is not None else " (client-side navigation)."), started, request=request)


def _test_currency_case(page, context, spec, request, started):
    if not spec.get("discovered"):
        _fail(page, spec, request, started, spec.get("discoveryNote", "Currency selector or option was not discovered."))

    before = page.evaluate(CURRENT_CURRENCY_SCRIPT)
    trigger = page.evaluate(CURRENCY_TRIGGER_SCRIPT)
    if not trigger.get("found"):
        _fail(page, spec, request, started, "The currency selector could not be found on the freshly opened homepage.")

    code = str(spec.get("currencyCode", "")).upper()
    label = str(spec.get("currencyLabel", code))
    before_prices = before.get("prices", [])
    try:
        if spec.get("currencyMode") == "select" or trigger.get("tag") == "select":
            selector = page.locator('[data-qa-currency-trigger="true"]')
            value = str(spec.get("currencyValue", ""))
            if value:
                selector.select_option(value=value, timeout=ACTION_TIMEOUT_MS)
            else:
                selector.select_option(label=label, timeout=ACTION_TIMEOUT_MS)
        else:
            page.locator('[data-qa-currency-trigger="true"]').click(timeout=ACTION_TIMEOUT_MS)
            page.wait_for_timeout(300)
            option_spec = dict(spec)
            option_spec["kind"] = "currency_option"
            option = _find_target(page, option_spec)
            if not option.get("found"):
                _fail(page, spec, request, started, f"Currency option {code} was not visible after opening the selector.")
            page.locator(f'[data-qa-target="{spec["id"]}"]').click(timeout=ACTION_TIMEOUT_MS)

        try:
            page.wait_for_load_state("domcontentloaded", timeout=2200)
        except PlaywrightError:
            pass
        page.wait_for_timeout(1100)
    except pytest.fail.Exception:
        raise
    except Exception as exc:
        _fail(page, spec, request, started, f"Could not select currency {code}: {type(exc).__name__}: {str(exc).splitlines()[0][:220]}")

    after = page.evaluate(CURRENT_CURRENCY_SCRIPT)
    current_code = str(after.get("code", "")).upper()
    url_lower = page.url.lower()
    # Keep separators outside a character range with an unescaped hyphen.
    # URLs may contain a currency code in the path or query string.
    url_confirms = bool(re.search(r"(?:^|[/_\-?&=])" + re.escape(code.lower()) + r"(?:$|[/_\-?#&=])", url_lower))
    prices_changed = before_prices != after.get("prices", []) and bool(before_prices or after.get("prices", []))
    explicit_selection = current_code == code or url_confirms
    already_active = str(before.get("code", "")).upper() == code and current_code == code

    if explicit_selection or prices_changed or already_active:
        evidence = []
        if current_code == code:
            evidence.append(f"header shows {code}")
        if url_confirms:
            evidence.append("URL confirms the selected currency/market")
        if prices_changed:
            evidence.append("visible price values changed")
        if already_active and not evidence:
            evidence.append(f"{code} was already the active currency")
        _record(spec, "PASS", f"Selected currency {code}; " + "; ".join(evidence) + f". URL={page.url}", started, request=request)
        return

    _fail(page, spec, request, started,
          f"Currency option {code} was clicked, but the selected currency could not be verified. "
          f"Before={before.get('code') or 'unknown'}; after={current_code or 'unknown'}; URL={page.url}.")


def test_homepage_case(browser_context, base_url: str, case_spec: dict[str, Any], request):
    """Run exactly one independent homepage check per parameterized case."""
    spec = dict(case_spec)
    started = time.monotonic()
    spec["baseUrl"] = base_url
    if spec.get("kind") == "setup_error":
        _fail(None, spec, request, started, spec.get("discoveryNote", "Test case discovery failed."))

    page = browser_context.new_page()
    page.set_default_timeout(ACTION_TIMEOUT_MS)
    page.set_default_navigation_timeout(NAVIGATION_TIMEOUT_MS)
    try:
        response = _open_home(page, base_url)
    except Exception as exc:
        _fail(page, spec, request, started, f"Could not open the homepage: {type(exc).__name__}: {str(exc).splitlines()[0][:240]}")
        return

    if not response or response.status >= 400:
        status = response.status if response else "no response"
        _fail(page, spec, request, started, f"Homepage returned HTTP {status}: {page.url}")

    if spec.get("kind") == "homepage_load":
        _record(spec, "PASS", f"Homepage loaded successfully: HTTP {response.status} — {page.url}", started, request=request)
        page.close()
        return

    try:
        if spec.get("kind") == "currency_discovery":
            _fail(page, spec, request, started, spec.get("discoveryNote", "Currency discovery failed."))
        if spec.get("kind") == "currency_option":
            _test_currency_case(page, browser_context, spec, request, started)
            return
        _test_navigation_case(page, browser_context, spec, base_url, request, started)
    finally:
        try:
            page.close()
        except PlaywrightError:
            pass
