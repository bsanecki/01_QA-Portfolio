"""Shared isolated checks for the T-shirt and mug collection sections."""
from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import pytest
from playwright.sync_api import Error as PlaywrightError

from config import ACTION_TIMEOUT_MS, NAVIGATION_TIMEOUT_MS, POST_CLICK_WAIT_MS
from ecomqa.reporting import write_result
from ecomqa.collection_testing import PRODUCT_LINKS_SCRIPT, VARIANT_CANDIDATES_SCRIPT


OPEN_COLLECTION_PRODUCT_SCRIPT = r"""(spec) => {
  const visible = (el) => {
    if (!el) return false;
    const style = getComputedStyle(el);
    const rect = el.getBoundingClientRect();
    return style.display !== 'none' && style.visibility !== 'hidden' && Number(style.opacity || 1) > 0 && rect.width > 0 && rect.height > 0;
  };
  const targetPath = (() => { try { return new URL(spec.productUrl, location.href).pathname.replace(/\/$/, ''); } catch (_) { return ''; } })();
  const anchors = [...document.querySelectorAll('a[href*="/products/"]')].filter(visible);
  const candidates = anchors.filter(a => {
    try { return new URL(a.href, location.href).pathname.replace(/\/$/, '') === targetPath; }
    catch (_) { return false; }
  });
  if (!candidates.length) return {found: false, detail: `Product card link was not found for ${targetPath}`};
  const target = candidates.find(a => a.querySelector('img')) || candidates[0];
  target.setAttribute('data-qa-collection-product-target', 'true');
  return {found: true, href: target.href, text: (target.innerText || target.getAttribute('aria-label') || '').replace(/\s+/g, ' ').trim()};
}"""

VARIANT_STATE_SCRIPT = r"""(index) => {
  const el = document.querySelector(`[data-qa-variant-index="${index}"]`);
  if (!el) return null;
  const input = el.matches('input') ? el : (el.querySelector('input[type="radio"]') || (el.htmlFor ? document.getElementById(el.htmlFor) : null));
  const cls = String(el.className || '');
  return {
    exists: true,
    selected: el.getAttribute('aria-pressed') === 'true' || el.getAttribute('aria-selected') === 'true' ||
      el.getAttribute('aria-checked') === 'true' || el.getAttribute('aria-current') === 'true' ||
      /(^|[-_\s])(active|selected|checked|current|is-active|is-selected)([-_\s]|$)/i.test(cls) || Boolean(input && input.checked),
    disabled: Boolean(el.disabled) || el.getAttribute('aria-disabled') === 'true',
    text: (el.innerText || el.getAttribute('aria-label') || el.value || '').replace(/\s+/g, ' ').trim(),
    className: cls
  };
}"""


def _console_line(request, message: str) -> None:
    """Write nested size results directly to pytest's terminal, even with output capture enabled."""
    try:
        reporter = request.config.pluginmanager.get_plugin("terminalreporter")
        if reporter:
            reporter.write_line(message)
    except Exception:
        pass


def _record(spec: dict[str, Any], status: str, details: str, started: float, screenshot: str | None = None, request=None) -> None:
    results_file = os.getenv("E2E_RESULTS_FILE")
    if not results_file:
        return
    write_result(results_file, {
        "id": spec.get("id", "unknown"),
        "kind": spec.get("kind", "unknown"),
        "label": spec.get("label", "Unnamed collection check"),
        "status": status,
        "details": details,
        "duration_ms": round((time.monotonic() - started) * 1000),
        "screenshot": screenshot,
    })


def _screenshot(page, spec: dict[str, Any]) -> str | None:
    root = os.getenv("E2E_SCREENSHOT_DIR")
    if not root or page is None:
        return None
    directory = Path(root)
    directory.mkdir(parents=True, exist_ok=True)
    safe_id = "".join(char if char.isalnum() or char in "-_" else "-" for char in spec.get("id", "failure"))[:100]
    path = directory / f"{safe_id}.png"
    try:
        page.screenshot(path=str(path), full_page=False, timeout=5_000)
        report_dir = os.getenv("E2E_REPORT_DIR")
        return str(path.relative_to(Path(report_dir))) if report_dir else str(path)
    except Exception:
        return None


def _fail(page, spec: dict[str, Any], started: float, details: str) -> None:
    screenshot = _screenshot(page, spec)
    _record(spec, "FAIL", details, started, screenshot)
    pytest.fail(details, pytrace=False)


def _skip(spec: dict[str, Any], started: float, details: str) -> None:
    _record(spec, "SKIP", details, started)
    pytest.skip(details)


def _dismiss_cookie_notice(page) -> None:
    """Dismiss a cookie banner in the isolated context so it cannot block the test target."""
    import re
    patterns = [
        re.compile(r"reject\s+all|only\s+necessary|essential\s+only|reject\s+optional|necessary\s+only|decline\s+optional", re.I),
        re.compile(r"accept\s+all|accept\s+cookies|allow\s+all|agree\s+and\s+continue", re.I),
    ]
    for pattern in patterns:
        try:
            buttons = page.get_by_role("button", name=pattern)
            for index in range(min(buttons.count(), 6)):
                button = buttons.nth(index)
                try:
                    if button.is_visible() and button.is_enabled():
                        button.click(timeout=900)
                        page.wait_for_timeout(120)
                        return
                except PlaywrightError:
                    continue
        except PlaywrightError:
            continue


def _normal_path(value: str) -> str:
    return urlsplit(value).path.rstrip("/")


def _safe_case_part(value: str) -> str:
    return "".join(char.lower() if char.isalnum() else "-" for char in value).strip("-")[:48] or "option"


def _matching_variant(candidates: list[dict[str, Any]], target: dict[str, Any]) -> dict[str, Any] | None:
    """Find the same size option in a freshly inspected product DOM."""
    target_type = str(target.get("type", "control"))
    target_label = str(target.get("label", "")).strip().casefold()
    target_group = str(target.get("group", "")).strip().casefold()
    target_value = str(target.get("value", ""))
    matches = [
        item for item in candidates
        if str(item.get("type", "control")) == target_type
        and str(item.get("label", "")).strip().casefold() == target_label
    ]
    if target_group:
        grouped = [item for item in matches if str(item.get("group", "")).strip().casefold() == target_group]
        if grouped:
            matches = grouped
    if target_value:
        valued = [item for item in matches if str(item.get("value", "")) == target_value]
        if valued:
            matches = valued
    return matches[0] if matches else None


def _click_variant_once(target_page, variant_snapshot: dict[str, Any]) -> str:
    """Click one option on the already-open product page, without navigating away."""
    label = str(variant_snapshot.get("label") or "").strip()
    current_options = target_page.evaluate(VARIANT_CANDIDATES_SCRIPT)
    current = _matching_variant(current_options, variant_snapshot)
    if current is None:
        raise AssertionError(f"Size/variant option '{label}' could not be found on the current product page.")

    variant_type = str(current.get("type", "control"))
    if variant_type == "select":
        select_index = int(current.get("selectIndex", -1))
        selector = target_page.locator(f'[data-qa-variant-select-index="{select_index}"]')
        if selector.count() != 1 or not selector.is_visible() or not selector.is_enabled():
            raise AssertionError(f"Size selector for '{label}' is missing, ambiguous, or disabled.")
        option_value = str(current.get("value") or "")
        if not option_value:
            raise AssertionError(f"Size option '{label}' has no selectable value.")
        selector.select_option(value=option_value, timeout=ACTION_TIMEOUT_MS)
        target_page.wait_for_timeout(250)
        selected_value = selector.input_value()
        if selected_value != option_value:
            raise AssertionError(
                f"Selecting '{label}' did not persist; expected value {option_value!r}, got {selected_value!r}."
            )
        return f"Selected size/variant '{label}' and verified the selected value."

    control_index = int(current.get("controlIndex", -1))
    selector = target_page.locator(f'[data-qa-variant-index="{control_index}"]')
    if selector.count() != 1 or not selector.is_visible() or not selector.is_enabled():
        raise AssertionError(f"Size option '{label}' is missing, ambiguous, or disabled.")

    before_state = target_page.evaluate(VARIANT_STATE_SCRIPT, control_index)
    if before_state is None or before_state.get("disabled"):
        raise AssertionError(f"Size option '{label}' is disabled before clicking.")
    selector.click(timeout=ACTION_TIMEOUT_MS)
    target_page.wait_for_timeout(300)

    after_options = target_page.evaluate(VARIANT_CANDIDATES_SCRIPT)
    after_match = _matching_variant(after_options, variant_snapshot)
    if after_match is None:
        raise AssertionError(f"Size option '{label}' disappeared after being clicked.")
    after_index = int(after_match.get("controlIndex", -1))
    after_state = target_page.evaluate(VARIANT_STATE_SCRIPT, after_index)
    if after_state is None:
        raise AssertionError(f"Could not verify the selected state for size option '{label}'.")
    if not after_state.get("selected"):
        raise AssertionError(f"Clicking size option '{label}' did not produce a verifiable selected state.")
    return f"Clicked size/variant '{label}' and verified that it is selected."


def _open_product_from_collection(page, context, spec: dict[str, Any], started: float) -> tuple[Any, str | None, int | None]:
    collection_url = spec.get("collectionUrl")
    if not collection_url:
        _fail(page, spec, started, "Collection URL was not supplied by discovery.")
    try:
        response = page.goto(collection_url, wait_until="domcontentloaded", timeout=NAVIGATION_TIMEOUT_MS)
        page.wait_for_timeout(350)
    except Exception as exc:
        _fail(page, spec, started, f"Could not open the collection page: {type(exc).__name__}: {str(exc).splitlines()[0][:220]}")
    if not response or response.status >= 400:
        _fail(page, spec, started, f"Collection page returned HTTP {response.status if response else 'no response'}: {page.url}")

    _dismiss_cookie_notice(page)
    found = page.evaluate(OPEN_COLLECTION_PRODUCT_SCRIPT, spec)
    if not found.get("found"):
        _fail(page, spec, started, found.get("detail", "Product card was not found in the collection."))

    responses: list[dict[str, Any]] = []
    popups: list[Any] = []

    def on_response(res, source_page=None):
        source_page = source_page or page
        try:
            if res.request.is_navigation_request() and res.frame == source_page.main_frame:
                responses.append({"url": res.url, "status": res.status})
        except PlaywrightError:
            pass

    page.on("response", lambda res: on_response(res, page))

    def on_popup(new_page):
        if new_page is page:
            return
        popups.append(new_page)
        new_page.on("response", lambda res: on_response(res, new_page))

    context.on("page", on_popup)
    before_url = page.url
    try:
        page.locator('[data-qa-collection-product-target="true"]').click(timeout=ACTION_TIMEOUT_MS)
    except PlaywrightError as exc:
        # A click can still navigate even if Playwright times out while waiting for the document.
        page.wait_for_timeout(350)
        if page.url == before_url and not popups:
            _fail(page, spec, started, f"Could not click the product card: {type(exc).__name__}: {str(exc).splitlines()[0][:220]}")
    page.wait_for_timeout(POST_CLICK_WAIT_MS)
    target_page = popups[-1] if popups else page
    try:
        target_page.wait_for_load_state("domcontentloaded", timeout=2_000)
    except PlaywrightError:
        pass
    after_url = target_page.url
    if "/products/" not in urlsplit(after_url).path.lower():
        _fail(target_page, spec, started, f"Product card did not open a product detail page. Landed on {after_url}.")
    response_status = next((item["status"] for item in reversed(responses) if _normal_path(item["url"]) == _normal_path(after_url)), None)
    if response_status is not None and response_status >= 400:
        _fail(target_page, spec, started, f"Product detail returned HTTP {response_status}: {after_url}")
    return target_page, after_url, response_status


def run_collection_case(browser_context, base_url: str, case_spec: dict[str, Any], request, expected_section: str) -> None:
    """Open one collection/product and test one selectable size option per case."""
    spec = dict(case_spec)
    started = time.monotonic()
    if spec.get("sectionKey") != expected_section:
        _fail(None, spec, started, f"Wrong section case routed to {expected_section}: {spec.get('sectionKey')!r}.")
    if spec.get("kind") == "setup_error" or not spec.get("discovered", True):
        _fail(None, spec, started, spec.get("discoveryNote", "Collection discovery failed."))
    if spec.get("kind") in ("duplicate_product_listing", "duplicate_product_title"):
        _fail(None, spec, started, spec.get("discoveryNote", "Potential repeated product title detected."))

    page = browser_context.new_page()
    target_page = page
    page.set_default_timeout(ACTION_TIMEOUT_MS)
    page.set_default_navigation_timeout(NAVIGATION_TIMEOUT_MS)
    try:
        if spec.get("kind") == "collection_page_load":
            try:
                response = page.goto(spec["collectionUrl"], wait_until="domcontentloaded", timeout=NAVIGATION_TIMEOUT_MS)
                page.wait_for_timeout(350)
            except Exception as exc:
                _fail(page, spec, started, f"Could not open the collection page: {type(exc).__name__}: {str(exc).splitlines()[0][:220]}")
            if not response or response.status >= 400:
                _fail(page, spec, started, f"Collection page returned HTTP {response.status if response else 'no response'}: {page.url}")
            links = page.evaluate(PRODUCT_LINKS_SCRIPT)
            _record(spec, "PASS", f"Collection loaded successfully: HTTP {response.status}; {len(links)} product card links detected; URL={page.url}.", started)
            return
        try:
            target_page, product_url, _ = _open_product_from_collection(page, browser_context, spec, started)
        except pytest.fail.Exception:
            raise
        except Exception as exc:
            _fail(page, spec, started, f"Could not open product from collection: {type(exc).__name__}: {str(exc).splitlines()[0][:220]}")
            return

        kind = spec.get("kind")
        product_label = spec.get("productLabel", "Product")
        if kind == "product_size_sweep":
            try:
                variants = target_page.evaluate(VARIANT_CANDIDATES_SCRIPT)
            except PlaywrightError as exc:
                _fail(target_page, spec, started, f"Could not inspect size options: {type(exc).__name__}: {str(exc).splitlines()[0][:220]}")

            if not variants:
                if spec.get("expectsSizes"):
                    details = "No selectable size options were found on this T-shirt product page."
                    _fail(target_page, spec, started, details)
                details = "No selectable size/capacity option is offered for this mug; no size click was required."
                _console_line(request, f"    [SIZE SKIP] {product_label}: no size/capacity option found")
                _record(spec, "SKIP", f"{details} URL={product_url}", started)
                pytest.skip(details)

            failures: list[str] = []
            for variant_index, variant_snapshot in enumerate(variants, 1):
                option_label = str(variant_snapshot.get("label") or "").strip() or f"option {variant_index}"
                option_group = str(variant_snapshot.get("group") or "").strip()
                option_spec = {
                    **spec,
                    "id": f"{spec['id']}-size-{variant_index:02d}-{_safe_case_part(option_label)}",
                    "kind": "size_click",
                    "label": f"Click size/variant '{option_label}' — {product_label}",
                }
                option_started = time.monotonic()
                try:
                    details = _click_variant_once(target_page, variant_snapshot)
                    if option_group:
                        details += f" Option group: {option_group}."
                    _record(option_spec, "PASS", details, option_started)
                    _console_line(request, f"    [SIZE PASS] {option_label} — {product_label}")
                except Exception as exc:
                    error = f"{type(exc).__name__}: {str(exc).splitlines()[0][:220]}"
                    screenshot = _screenshot(target_page, option_spec)
                    _record(option_spec, "FAIL", f"Could not click size/variant '{option_label}': {error}", option_started, screenshot)
                    failures.append(f"{option_label}: {error}")
                    _console_line(request, f"    [SIZE FAIL] {option_label} — {product_label}: {error}")
                    # Do not stop at the first failed size. Try every remaining size on this same page.

            if failures:
                summary = (
                    f"Opened product once and attempted all {len(variants)} detected size/variant options; "
                    f"{len(failures)} failed. " + " | ".join(failures[:8])
                )
                # Fail the pytest product workflow, but do not add a second parent result row:
                # the failed size option(s) above are already individually recorded.
                _console_line(request, f"    [PRODUCT FAIL] {product_label}: {len(failures)}/{len(variants)} size checks failed")
                pytest.fail(summary, pytrace=False)

            _console_line(request, f"    [PRODUCT PASS] {product_label}: opened once; {len(variants)} size option(s) passed")
            return

        if kind == "product_open":
            if target_page is not page:
                try:
                    target_page.close()
                except PlaywrightError:
                    pass
                if _normal_path(page.url) != _normal_path(spec["collectionUrl"]):
                    _fail(page, spec, started, f"Product opened in a new tab, but the collection tab changed unexpectedly: {page.url}")
                _record(spec, "PASS", f"Product opened in a new tab ({product_url}); closing it returned control to the collection.", started)
                return
            try:
                returned = target_page.go_back(wait_until="domcontentloaded", timeout=NAVIGATION_TIMEOUT_MS)
                target_page.wait_for_timeout(250)
            except Exception as exc:
                _fail(target_page, spec, started, f"Product opened, but returning to the collection failed: {type(exc).__name__}: {str(exc).splitlines()[0][:200]}")
            if _normal_path(target_page.url) != _normal_path(spec["collectionUrl"]):
                _fail(target_page, spec, started, f"Browser did not return to the collection. Current URL: {target_page.url}")
            status = returned.status if returned else None
            if status is not None and status >= 400:
                _fail(target_page, spec, started, f"Returning to the collection returned HTTP {status}: {target_page.url}")
            _record(spec, "PASS", f"Opened product from collection and returned successfully. Product URL: {product_url}; collection URL: {target_page.url}.", started)
            return

        if kind in ("variant_discovery", "product_variant"):
            variants = target_page.evaluate(VARIANT_CANDIDATES_SCRIPT)
            if kind == "variant_discovery":
                if variants:
                    _fail(target_page, spec, started, f"Discovery originally found no selectable size options, but {len(variants)} were detected at runtime. The discovery inventory is inconsistent.")
                if spec.get("expectsSizes"):
                    _fail(target_page, spec, started, "No selectable size options were found on a T-shirt product page.")
                _skip(spec, started, "This mug has no selectable size/capacity option; there is no size control to click.")

            variant_type = spec.get("variantType", "control")
            label = str(spec.get("variantLabel", "")).strip()
            group = str(spec.get("variantGroup", "")).strip()
            candidates = [item for item in variants if item.get("type") == variant_type and str(item.get("label", "")).strip().casefold() == label.casefold()]
            if group:
                group_matches = [item for item in candidates if str(item.get("group", "")).strip().casefold() == group.casefold()]
                if group_matches:
                    candidates = group_matches
            if not candidates:
                _fail(target_page, spec, started, f"Size/variant option '{label}' was not found on the opened product page.")

            if variant_type == "select":
                select_index = int(spec.get("variantSelectIndex", candidates[0].get("selectIndex", -1)))
                selector = target_page.locator(f'[data-qa-variant-select-index="{select_index}"]')
                if selector.count() != 1:
                    _fail(target_page, spec, started, f"Could not uniquely locate the size selector for '{label}' (matches={selector.count()}).")
                option_value = str(spec.get("variantValue") or candidates[0].get("value") or "")
                if not option_value:
                    _fail(target_page, spec, started, f"Size option '{label}' has no selectable value.")
                try:
                    selector.select_option(value=option_value, timeout=ACTION_TIMEOUT_MS)
                    target_page.wait_for_timeout(250)
                except PlaywrightError as exc:
                    _fail(target_page, spec, started, f"Could not select size '{label}': {type(exc).__name__}: {str(exc).splitlines()[0][:200]}")
                selected_value = selector.input_value()
                if selected_value != option_value:
                    _fail(target_page, spec, started, f"Size selection did not persist. Expected value {option_value!r}; current value {selected_value!r}.")
            else:
                control_index = int(spec.get("variantControlIndex", candidates[0].get("controlIndex", -1)))
                selector = target_page.locator(f'[data-qa-variant-index="{control_index}"]')
                if selector.count() != 1 or not selector.is_visible():
                    # Fall back to the index discovered from the current DOM if the ordering changed.
                    control_index = int(candidates[0].get("controlIndex", -1))
                    selector = target_page.locator(f'[data-qa-variant-index="{control_index}"]')
                if selector.count() != 1 or not selector.is_visible():
                    _fail(target_page, spec, started, f"Could not uniquely locate selectable option '{label}' (matches={selector.count()}).")
                before_state = target_page.evaluate(VARIANT_STATE_SCRIPT, control_index)
                if before_state is None or before_state.get("disabled"):
                    _fail(target_page, spec, started, f"Size option '{label}' is missing or disabled before clicking.")
                try:
                    selector.click(timeout=ACTION_TIMEOUT_MS)
                    target_page.wait_for_timeout(350)
                except PlaywrightError as exc:
                    _fail(target_page, spec, started, f"Clicking size '{label}' failed: {type(exc).__name__}: {str(exc).splitlines()[0][:200]}")
                target_page.evaluate(VARIANT_CANDIDATES_SCRIPT)
                after_state = target_page.evaluate(VARIANT_STATE_SCRIPT, control_index)
                if after_state is None:
                    _fail(target_page, spec, started, f"Size option '{label}' disappeared after clicking.")
                if not before_state.get("selected") and not after_state.get("selected"):
                    _fail(target_page, spec, started, f"Clicking size '{label}' produced no verifiable selected state.")

            _record(spec, "PASS", f"Size/variant option '{label}' was clickable and selection was verified on {product_label}.", started)
            return

        _fail(target_page, spec, started, f"Unsupported collection test kind: {kind!r}.")
    finally:
        if target_page is not page:
            try:
                target_page.close()
            except PlaywrightError:
                pass
        try:
            page.close()
        except PlaywrightError:
            pass
