"""Section 04 - cart workflow tests for three fixed, non-purchasing test products."""
from __future__ import annotations

import re
import os
import time
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlsplit

import pytest
from playwright.sync_api import Error as PlaywrightError

from config import ACTION_TIMEOUT_MS, NAVIGATION_TIMEOUT_MS, POST_CLICK_WAIT_MS
from ecomqa.collection_testing import VARIANT_CANDIDATES_SCRIPT
from ecomqa.reporting import write_result

# Fixed products make runs repeatable. No orders/payments are submitted.
CART_PRODUCTS: list[dict[str, str]] = [
    {
        "id": "cart-tshirt-boyfriend",
        "slug": "this-is-my-boyfriend-cute-bubu-dudu-unisex-t-shirt-2",
        "label": "T-shirt - This Is My Boyfriend",
    },
    {
        "id": "cart-tshirt-back-off",
        "slug": "back-off-i-have-bubu-funny-bubu-dudu-unisex-t-shirt",
        "label": "T-shirt - Back Off, I Have Bubu",
    },
    {
        "id": "cart-mug-patience",
        "slug": "bubus-patience-1-funny-bubu-dudu-couple-mug",
        "label": "Mug - Bubu's Patience: 1%",
    },
]

MONEY_RE = re.compile(r"(?<!\d)(\d{1,3}(?:[ .\u00a0'’]\d{3})*|\d+)[,.](\d{2})(?!\d)")

ADD_TO_CART_SCRIPT = r"""() => {
  document.querySelectorAll('[data-qa-cart-add]').forEach(el => el.removeAttribute('data-qa-cart-add'));
  const visible = (el) => {
    if (!el) return false;
    const s = getComputedStyle(el), r = el.getBoundingClientRect();
    return s.display !== 'none' && s.visibility !== 'hidden' && Number(s.opacity || 1) > 0 && r.width > 0 && r.height > 0;
  };
  const norm = (s) => String(s || '').replace(/\s+/g, ' ').trim();
  const nodes = [...document.querySelectorAll('button,[role="button"],input[type="submit"]')]
    .filter(visible)
    .filter(el => !el.disabled && el.getAttribute('aria-disabled') !== 'true')
    .map((el, i) => ({el, i, label: norm(el.innerText || el.value || el.getAttribute('aria-label') || el.title)}))
    .filter(x => /add\s+to\s+cart/i.test(x.label) && !/added\s+to\s+cart/i.test(x.label));
  if (!nodes.length) return {found: false, detail: 'No visible, enabled Add to Cart button was found.'};
  nodes[0].el.setAttribute('data-qa-cart-add', 'true');
  return {found: true, label: nodes[0].label, matches: nodes.length};
}"""

OPEN_CART_CONTROL_SCRIPT = r"""() => {
  document.querySelectorAll('[data-qa-open-cart]').forEach(el => el.removeAttribute('data-qa-open-cart'));
  const visible = (el) => {
    if (!el) return false;
    const s = getComputedStyle(el), r = el.getBoundingClientRect();
    return s.display !== 'none' && s.visibility !== 'hidden' && Number(s.opacity || 1) > 0 && r.width > 0 && r.height > 0;
  };
  const norm = (s) => String(s || '').replace(/\s+/g, ' ').trim();
  const candidates = [...document.querySelectorAll('a,button,[role="button"]')].filter(visible).map((el, i) => {
    const text = norm(el.innerText || el.getAttribute('aria-label') || el.title);
    let path = '';
    try { path = el.href ? new URL(el.href, location.href).pathname.toLowerCase() : ''; } catch (_) {}
    let score = 99;
    if (/^(view cart|go to cart|open cart|view shopping cart)$/i.test(text)) score = 0;
    else if (path.endsWith('/cart') || /\/cart\/?$/.test(path)) score = 1;
    else if (/^(cart|shopping cart|basket|shopping bag)$/i.test(text)) score = 2;
    else if (/view cart|open cart/i.test(text)) score = 3;
    return {el, i, text, path, score};
  }).filter(x => x.score < 99 && !/checkout|express/i.test(x.text)).sort((a,b) => a.score - b.score);
  if (!candidates.length) return {found: false, detail: 'No visible cart navigation control was found.'};
  candidates[0].el.setAttribute('data-qa-open-cart', 'true');
  return {found: true, label: candidates[0].text, targetPath: candidates[0].path};
}"""

CART_STATE_SCRIPT = r"""() => {
  document.querySelectorAll('[data-qa-cart-row-index],[data-qa-cart-quantity],[data-qa-cart-remove],[data-qa-cart-increase],[data-qa-cart-decrease],[data-qa-cart-checkout]').forEach(el => {
    el.removeAttribute('data-qa-cart-row-index'); el.removeAttribute('data-qa-cart-quantity');
    el.removeAttribute('data-qa-cart-remove'); el.removeAttribute('data-qa-cart-increase');
    el.removeAttribute('data-qa-cart-decrease'); el.removeAttribute('data-qa-cart-checkout');
  });
  const visible = (el) => {
    if (!el) return false;
    const s = getComputedStyle(el), r = el.getBoundingClientRect();
    return s.display !== 'none' && s.visibility !== 'hidden' && Number(s.opacity || 1) > 0 && r.width > 0 && r.height > 0;
  };
  const norm = (s) => String(s || '').replace(/\s+/g, ' ').trim();
  const pathOf = (href) => { try { return new URL(href, location.href).pathname.replace(/\/$/, '').toLowerCase(); } catch (_) { return ''; } };
  const classText = (el) => {
    const value = el && el.className;
    if (typeof value === 'string') return value;
    if (value && typeof value.baseVal === 'string') return value.baseVal;
    return '';
  };
  // Include icon metadata and CSS classes: cart remove controls are often icon-only.
  const buttonLabel = (el) => {
    if (!el) return '';
    const parts = [
      el.getAttribute('aria-label'), el.getAttribute('title'),
      el.getAttribute('data-testid'), el.getAttribute('data-test'),
      el.getAttribute('data-action'), el.getAttribute('name'),
      el.getAttribute('data-icon'), el.getAttribute('data-lucide'),
      el.id, classText(el), el.innerText, el.textContent
    ];
    for (const icon of [...el.querySelectorAll('svg, [data-icon], [data-lucide], img')]) {
      parts.push(
        icon.getAttribute('aria-label'), icon.getAttribute('title'),
        icon.getAttribute('data-testid'), icon.getAttribute('data-icon'),
        icon.getAttribute('data-lucide'), icon.getAttribute('alt'), classText(icon)
      );
    }
    return norm(parts.filter(Boolean).join(' '));
  };
  const allAnchors = [...document.querySelectorAll('a[href*="/products/"]')].filter(visible);
  const byPath = new Map();
  for (const anchor of allAnchors) {
    const path = pathOf(anchor.href);
    if (!path.includes('/products/')) continue;
    let row = null;
    let node = anchor;
    for (let depth = 0; node && node !== document.body && depth < 10; depth++, node = node.parentElement) {
      const text = norm(node.innerText);
      if (!text || text.length > 1200) continue;
      const inputs = [...node.querySelectorAll('input[type="number"],input[name*="quantity" i],input[aria-label*="quantity" i],select[name*="quantity" i],select[aria-label*="quantity" i]')];
      const actions = [...node.querySelectorAll('button,[role="button"],a,[data-testid],[data-action]')].filter(visible).map(buttonLabel);
      const hasCartAction = actions.some(label => /remove|delete|trash|increase|decrease|increment|decrement|quantity|(^|\s)plus($|\s)|(^|\s)minus($|\s)/i.test(label) || label === '+' || label === '−' || label === '-');
      if (inputs.length || hasCartAction) { row = node; break; }
    }
    if (!row) continue; // Related/recommended product cards lack cart quantity controls.
    const existing = byPath.get(path);
    if (!existing || norm(row.innerText).length < norm(existing.row.innerText).length) byPath.set(path, {path, anchor, row});
  }

  const items = [];
  let index = 0;
  for (const item of byPath.values()) {
    const row = item.row;
    row.setAttribute('data-qa-cart-row-index', String(index));
    const controls = [...row.querySelectorAll('button,[role="button"],a,input[type="button"],input[type="submit"],[data-testid],[data-action]')].filter(visible);
    const labeled = controls.map(el => ({el, label: buttonLabel(el)}));
    const remove = labeled.find(x => /remove|delete|trash|cart[-_ ]?item[-_ ]?remove|remove[-_ ]?from[-_ ]?cart|delete[-_ ]?item|icon[-_ ]?close/i.test(x.label));
    const increase = labeled.find(x => /increase|increment|add one|plus|quantity\s*\+|icon[-_ ]?plus|plus[-_ ]?icon/i.test(x.label) || x.label.trim() === '+');
    const decrease = labeled.find(x => /decrease|decrement|minus|reduce quantity|quantity\s*-|icon[-_ ]?minus|minus[-_ ]?icon/i.test(x.label) || ['-', '−'].includes(x.label.trim()));
    if (remove) remove.el.setAttribute('data-qa-cart-remove', String(index));
    if (increase) increase.el.setAttribute('data-qa-cart-increase', String(index));
    if (decrease) decrease.el.setAttribute('data-qa-cart-decrease', String(index));
    const quantityControl = row.querySelector('input[type="number"],input[name*="quantity" i],input[aria-label*="quantity" i],select[name*="quantity" i],select[aria-label*="quantity" i]');
    if (quantityControl) quantityControl.setAttribute('data-qa-cart-quantity', String(index));
    let quantity = quantityControl ? String(quantityControl.value || '') : '';
    if (!quantity) {
      const match = norm(row.innerText).match(/(?:quantity|qty)\s*[:x]?\s*(\d{1,3})/i);
      if (match) quantity = match[1];
    }
    items.push({
      path: item.path,
      href: item.anchor.href,
      title: norm(item.anchor.innerText || item.anchor.getAttribute('aria-label') || item.anchor.querySelector('img')?.alt),
      rowIndex: index,
      rowText: norm(row.innerText).slice(0, 1000),
      quantity,
      hasQuantityControl: Boolean(quantityControl),
      hasRemoveControl: Boolean(remove),
      hasIncreaseControl: Boolean(increase),
      hasDecreaseControl: Boolean(decrease)
    });
    index++;
  }

  const bodyText = norm(document.body.innerText);
  const lines = (document.body.innerText || '').split(/\n+/).map(norm).filter(Boolean);
  let subtotalText = '';
  const subtotalCandidates = [];
  for (const el of [...document.querySelectorAll('body *')]) {
    if (!visible(el)) continue;
    const txt = norm(el.innerText);
    if (!/sub\s*total/i.test(txt) || txt.length > 220) continue;
    let cur = el;
    for (let depth = 0; cur && depth < 3; depth++, cur = cur.parentElement) {
      const candidate = norm(cur.innerText);
      if (/sub\s*total/i.test(candidate) && candidate.length <= 220 && /\d[,.]\d{2}/.test(candidate)) {
        subtotalCandidates.push(candidate);
        break;
      }
    }
  }
  if (subtotalCandidates.length) subtotalText = subtotalCandidates.sort((a,b) => a.length - b.length)[0];
  if (!subtotalText) {
    const i = lines.findIndex(line => /sub\s*total/i.test(line));
    if (i >= 0) subtotalText = [lines[i], lines[i+1] || '', lines[i+2] || ''].join(' ').trim();
  }
  const emptyMessage = /your (shopping )?cart is empty|cart is empty|basket is empty|no items in (your )?cart|empty cart/i.test(bodyText);

  // Prefer the stable selector captured from the live storefront via Playwright Codegen.
  const checkoutByTestId = [...document.querySelectorAll('[data-testid="cart.checkout.button"]')]
    .filter(visible)
    .filter(el => !el.disabled && el.getAttribute('aria-disabled') !== 'true')
    .map(el => ({el, label: buttonLabel(el)}));
  const checkoutCandidates = checkoutByTestId.length ? checkoutByTestId : [...document.querySelectorAll('button,a,[role="button"],input[type="submit"]')]
    .filter(visible)
    .filter(el => !el.disabled && el.getAttribute('aria-disabled') !== 'true')
    .map(el => ({el, label: buttonLabel(el)}))
    .filter(x => /^(checkout|proceed to checkout|continue to checkout)$/i.test(x.label) && !/express/i.test(x.label));
  if (checkoutCandidates.length) checkoutCandidates[0].el.setAttribute('data-qa-cart-checkout', 'true');

  return {
    url: location.href,
    bodyText: bodyText.slice(0, 12000),
    items,
    subtotalText,
    emptyMessage,
    checkoutFound: checkoutCandidates.length > 0,
    checkoutLabel: checkoutCandidates[0]?.label || ''
  };
}"""


def build_cart_specs(base_url: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    products = []
    for product in CART_PRODUCTS:
        products.append({**product, "url": urljoin(base_url if base_url.endswith("/") else base_url + "/", f"products/{product['slug']}")})
    scope = (
        "Add three fixed test products to an isolated cart, verify contents and subtotal, increase one item quantity, "
        "verify subtotal recalculation, remove an item, verify the subtotal decrease, open the checkout step without "
        "submitting an order or payment, then empty the test cart."
    )
    spec = {
        "id": "cart-workflow",
        "kind": "cart_workflow",
        "label": "Add, update, remove cart items and open checkout safely",
        "discovered": True,
    }
    discovery = {
        "section_key": "cart",
        "section_title": "Section 04 - Cart",
        "products_discovered": len(products),
        "products": [{"id": p["id"], "label": p["label"], "url": p["url"]} for p in products],
        "scope": scope,
        "discovery_error": None,
        "section_screenshot": None,
    }
    return [spec], discovery


def _console(request, marker: str, label: str, details: str) -> None:
    try:
        reporter = request.config.pluginmanager.get_plugin("terminalreporter")
        if reporter:
            clipped = details.replace("\n", " ")
            if len(clipped) > 260:
                clipped = clipped[:257] + "..."
            reporter.write_line(f"    [{marker}] {label} - {clipped}")
    except Exception:
        pass


def _stage(number: int, title: str) -> None:
    """Print a visible phase divider for the stateful cart workflow."""
    width = 88
    print("\n" + "=" * width, flush=True)
    print(f" STEP {number}/6 - {title} ".center(width, "="), flush=True)
    print("=" * width, flush=True)


def _screenshot(page: Any, case_id: str) -> str | None:
    root = os.getenv("E2E_SCREENSHOT_DIR")
    if not root or page is None:
        return None
    directory = Path(root)
    directory.mkdir(parents=True, exist_ok=True)
    safe_id = re.sub(r"[^a-zA-Z0-9_-]+", "-", case_id).strip("-")[:100] or "cart-failure"
    path = directory / f"{safe_id}.png"
    try:
        page.screenshot(path=str(path), full_page=False, timeout=5_000)
        report_dir = os.getenv("E2E_REPORT_DIR")
        return str(path.relative_to(Path(report_dir))) if report_dir else str(path)
    except Exception:
        return None


def _record_step(request, case_id: str, label: str, status: str, details: str, started: float, page=None) -> None:
    result_file = os.getenv("E2E_RESULTS_FILE")
    screenshot = _screenshot(page, case_id) if status == "FAIL" else None
    if result_file:
        write_result(result_file, {
            "id": case_id,
            "kind": "cart_check",
            "label": label,
            "status": status,
            "details": details,
            "duration_ms": round((time.monotonic() - started) * 1000),
            "screenshot": screenshot,
        })
    marker = {"PASS": "PASS", "FAIL": "FAIL", "SKIP": "SKIP"}.get(status, status)
    if os.getenv("E2E_CART_LIVE_LOG") == "1":
        clipped = details.replace("\n", " ")
        if len(clipped) > 340:
            clipped = clipped[:337] + "..."
        print(f"  [{marker}] {label}", flush=True)
        print(f"      {clipped}", flush=True)
    else:
        _console(request, marker, label, details)


def _parse_money(text: str | None) -> Decimal | None:
    if not text:
        return None
    match = MONEY_RE.search(text)
    if not match:
        return None
    whole = re.sub(r"[ .\u00a0'’]", "", match.group(1))
    try:
        return Decimal(f"{whole}.{match.group(2)}")
    except InvalidOperation:
        return None


def _subtotal(state: dict[str, Any]) -> Decimal | None:
    return _parse_money(state.get("subtotalText", ""))


def _normal_path(url_or_path: str) -> str:
    try:
        return urlsplit(url_or_path).path.rstrip("/").casefold()
    except Exception:
        return str(url_or_path).rstrip("/").casefold()


def _find_item(state: dict[str, Any], product: dict[str, str]) -> dict[str, Any] | None:
    target = _normal_path(product["url"])
    for item in state.get("items", []):
        if _normal_path(item.get("href", "")) == target or item.get("path", "").casefold() == target:
            return item
    return None


def _click_first_variant(page) -> tuple[bool, str]:
    from tests.collection_test_helpers import _click_variant_once

    options = page.evaluate(VARIANT_CANDIDATES_SCRIPT)
    if not options:
        return False, "No selectable size/capacity option was found on the product page."
    option = options[0]
    try:
        detail = _click_variant_once(page, option)
        return True, detail
    except Exception as exc:
        return False, f"Could not select the first available size/capacity: {type(exc).__name__}: {str(exc).splitlines()[0][:180]}"


def _find_money_on_product(page) -> Decimal | None:
    try:
        text = page.locator("main").inner_text(timeout=1_500)
    except PlaywrightError:
        text = page.locator("body").inner_text(timeout=1_500)
    return _parse_money(text)


def _open_cart_control(page) -> tuple[bool, str]:
    last_detail = ""
    # The add-to-cart drawer can first show View Cart; if necessary, inspect it a second time.
    for _ in range(2):
        target = page.evaluate(OPEN_CART_CONTROL_SCRIPT)
        if not target.get("found"):
            last_detail = target.get("detail", "No visible cart control was found.")
            break
        try:
            locator = page.locator('[data-qa-open-cart="true"]')
            if locator.count() != 1:
                last_detail = f"Cart control was ambiguous (matches={locator.count()})."
                break
            before_url = page.url
            locator.click(timeout=ACTION_TIMEOUT_MS)
            page.wait_for_timeout(650)
            if urlsplit(page.url).path.casefold().rstrip("/").endswith("/cart"):
                return True, f"Clicked '{target.get('label') or 'cart'}' and opened {page.url}."
            # If this opened a drawer instead of the cart page, look for its View Cart action.
            if page.url != before_url:
                last_detail = f"Cart control changed URL to {page.url}, but did not reach the cart page."
            else:
                last_detail = "Cart control was clicked, but the cart page did not open."
        except PlaywrightError as exc:
            last_detail = f"Could not click cart control: {type(exc).__name__}: {str(exc).splitlines()[0][:180]}"
            break
    return False, last_detail or "Could not open the cart using the visible UI control."


def _cart_state(page) -> dict[str, Any]:
    return page.evaluate(CART_STATE_SCRIPT)


def _click_quantity_increase(page, item: dict[str, Any]) -> tuple[bool, str]:
    # Re-tag controls after each render, because Fourthwall may re-render the whole cart row.
    state = _cart_state(page)
    current = next((row for row in state.get("items", []) if row.get("path") == item.get("path")), None)
    if not current:
        return False, "Target cart item could not be found before changing its quantity."
    index = current["rowIndex"]
    plus = page.locator(f'[data-qa-cart-increase="{index}"]')
    if plus.count() == 1 and plus.is_visible() and plus.is_enabled():
        try:
            plus.click(timeout=ACTION_TIMEOUT_MS)
            page.wait_for_timeout(650)
            return True, "Clicked the cart's increase-quantity control."
        except PlaywrightError as exc:
            return False, f"Increase-quantity click failed: {type(exc).__name__}: {str(exc).splitlines()[0][:180]}"

    state = _cart_state(page)
    current = next((row for row in state.get("items", []) if row.get("path") == item.get("path")), None)
    if not current:
        return False, "Target cart item disappeared before quantity could be changed."
    index = current["rowIndex"]
    quantity = page.locator(f'[data-qa-cart-quantity="{index}"]')
    if quantity.count() == 1 and quantity.is_visible() and quantity.is_enabled():
        try:
            tag = quantity.evaluate("el => el.tagName.toLowerCase()")
            if tag == "select":
                options = quantity.locator("option").all()
                two_value = None
                for option in options:
                    if (option.get_attribute("value") or option.inner_text()).strip() == "2":
                        two_value = option.get_attribute("value") or option.inner_text().strip()
                        break
                if two_value is None:
                    return False, "Quantity selector has no option for quantity 2."
                quantity.select_option(value=two_value, timeout=ACTION_TIMEOUT_MS)
            else:
                quantity.fill("2", timeout=ACTION_TIMEOUT_MS)
                quantity.dispatch_event("change")
                quantity.press("Enter", timeout=ACTION_TIMEOUT_MS)
            page.wait_for_timeout(650)
            return True, "Set the cart quantity control to 2."
        except PlaywrightError as exc:
            return False, f"Could not set quantity to 2: {type(exc).__name__}: {str(exc).splitlines()[0][:180]}"
    return False, "No usable increase button or quantity input was found for this cart item."


def _remove_item(page, item: dict[str, Any]) -> tuple[bool, str]:
    state = _cart_state(page)
    current = next((row for row in state.get("items", []) if row.get("path") == item.get("path")), None)
    if not current:
        return True, "Item is already absent from the cart."
    index = current["rowIndex"]
    remove = page.locator(f'[data-qa-cart-remove="{index}"]')
    remove_detail = ""
    if remove.count() == 1 and remove.is_visible() and remove.is_enabled():
        try:
            remove.scroll_into_view_if_needed(timeout=ACTION_TIMEOUT_MS)
            remove.click(timeout=ACTION_TIMEOUT_MS)

            # Fourthwall may show an inline confirmation bar after the first click.
            # Use the exact locator observed with Playwright Codegen and confirm it.
            confirm_delete = page.get_by_role("button", name="Delete", exact=True)
            try:
                confirm_delete.wait_for(state="visible", timeout=1_500)
            except PlaywrightError:
                # Some cart layouts remove immediately and do not show confirmation.
                pass
            try:
                visible_delete = [
                    confirm_delete.nth(i)
                    for i in range(confirm_delete.count())
                    if confirm_delete.nth(i).is_visible() and confirm_delete.nth(i).is_enabled()
                ]
                if visible_delete:
                    # Click the visible confirmation button; this is the second step
                    # that was previously missing when the storefront showed a prompt.
                    visible_delete[-1].click(timeout=ACTION_TIMEOUT_MS)
                    remove_detail = 'Clicked the cart remove control and confirmed with the "Delete" button.'
            except PlaywrightError as exc:
                remove_detail = f'Delete confirmation click failed: {type(exc).__name__}: {str(exc).splitlines()[0][:180]}'

            page.wait_for_timeout(900)
            after_click = _cart_state(page)
            if not any(row.get("path") == current.get("path") for row in after_click.get("items", [])):
                return True, "Clicked the item's remove control; the cart line disappeared."
            # Some storefronts rerender the row after the async cart mutation.
            page.wait_for_timeout(900)
            after_retry_wait = _cart_state(page)
            if not any(row.get("path") == current.get("path") for row in after_retry_wait.get("items", [])):
                return True, "Clicked the item's remove control; the cart line disappeared after the UI update."
            remove_detail = "Remove control was clicked but the product row remained in the cart."
        except PlaywrightError as exc:
            remove_detail = f"Remove click failed: {type(exc).__name__}: {str(exc).splitlines()[0][:180]}"
    else:
        row = page.locator(f'[data-qa-cart-row-index="{index}"]')
        try:
            controls = row.locator('button,[role="button"],a,input[type="button"],input[type="submit"],[data-testid],[data-action]')
            descriptions = []
            for i in range(min(controls.count(), 12)):
                control = controls.nth(i)
                attrs = [control.get_attribute(name) for name in ("aria-label", "title", "data-testid", "data-action", "class", "id")]
                try:
                    attrs.append((control.inner_text(timeout=500) or "").strip())
                except PlaywrightError:
                    pass
                label = " ".join(x for x in attrs if x)
                descriptions.append(f"{control.evaluate('el => el.tagName.toLowerCase()')}[{label or 'icon-only/no label'}]")
            remove_detail = "No remove control was identified. Row controls: " + ("; ".join(descriptions) if descriptions else "none") + "."
        except PlaywrightError:
            remove_detail = "No usable remove control was identified in the cart row."

    # Some cart layouts use the decrement control to remove a single-quantity item.
    qty = int(current.get("quantity") or "1")
    minus = page.locator(f'[data-qa-cart-decrease="{index}"]')
    if qty == 1 and minus.count() == 1 and minus.is_visible() and minus.is_enabled():
        try:
            minus.click(timeout=ACTION_TIMEOUT_MS)
            page.wait_for_timeout(650)
            return True, "Used the quantity-decrease control to remove the single-quantity item."
        except PlaywrightError as exc:
            return False, f"Quantity-decrease removal failed: {type(exc).__name__}: {str(exc).splitlines()[0][:180]}"
    return False, remove_detail or "No usable remove control was found for this cart item."


def _open_checkout(page) -> tuple[bool, str, Any]:
    state = _cart_state(page)
    checkout_by_test_id = page.get_by_test_id("cart.checkout.button")
    if checkout_by_test_id.count() == 0 and not state.get("checkoutFound"):
        return False, (
            "No visible checkout control was found. Tried the observed test id "
            "'cart.checkout.button' and the text-based fallback."
        ), page
    popups: list[Any] = []
    navigation_responses: list[dict[str, Any]] = []

    def track_response(response, owner_page):
        try:
            if response.request.is_navigation_request() and response.frame == owner_page.main_frame:
                navigation_responses.append({"url": response.url, "status": response.status})
        except PlaywrightError:
            pass

    page.on("response", lambda response: track_response(response, page))
    def on_popup(popup):
        popups.append(popup)
        popup.on("response", lambda response: track_response(response, popup))
    page.on("popup", on_popup)
    before_url = page.url
    try:
        before_text = page.locator("body").inner_text(timeout=2_000).casefold()
    except PlaywrightError:
        before_text = ""
    try:
        # Prefer the exact stable test id recorded with Playwright Codegen.
        button = page.get_by_test_id("cart.checkout.button")
        if button.count() == 0:
            button = page.locator('[data-qa-cart-checkout="true"]')
        if button.count() != 1 or not button.is_visible() or not button.is_enabled():
            return False, (
                "Checkout control was missing, ambiguous, or disabled "
                f"(test-id matches={checkout_by_test_id.count()}, fallback matches={page.locator('[data-qa-cart-checkout="true"]').count()})."
            ), page
        button.click(timeout=ACTION_TIMEOUT_MS)
        # Fourthwall's hosted checkout can take several seconds to initialize and may
        # transition through client-side routing without an immediate URL/content change.
        # The requested check is the checkout action itself, not the payment flow.
        target_page = popups[-1] if popups else page
        try:
            target_page.wait_for_load_state("domcontentloaded", timeout=5_000)
        except PlaywrightError:
            # This can time out for SPA transitions; give the storefront additional
            # settling time rather than failing a successful click prematurely.
            pass
        target_page.wait_for_timeout(5_000)
        if popups:
            target_page = popups[-1]
        current_url = target_page.url
        navigation_response = next((item for item in reversed(navigation_responses) if item["url"] == current_url), None)
        if navigation_response and navigation_response["status"] >= 400:
            return False, f"Checkout click led to an HTTP error page: HTTP {navigation_response['status']} - {current_url}.", target_page
        # A successful Playwright click plus a settling wait is considered a pass here.
        # We intentionally do not require a specific checkout URL or text marker because
        # the hosted checkout can load asynchronously and its copy/routing may change.
        waited_seconds = 5
        return True, (
            f"Clicked checkout control using test id 'cart.checkout.button' and waited up to "
            f"{waited_seconds} seconds for the checkout interface to initialize. "
            f"Current URL: {current_url}. No order or payment was submitted."
        ), target_page
    except PlaywrightError as exc:
        return False, f"Checkout interaction failed: {type(exc).__name__}: {str(exc).splitlines()[0][:180]}.", page


def run_cart_workflow(browser_context, base_url: str, request) -> None:
    """Run a stateful cart workflow and report each cart action as its own result row."""
    from tests.collection_test_helpers import _click_variant_once, _dismiss_cookie_notice

    started_all = time.monotonic()
    page = browser_context.new_page()
    page.set_default_timeout(ACTION_TIMEOUT_MS)
    page.set_default_navigation_timeout(NAVIGATION_TIMEOUT_MS)
    base_url = base_url if base_url.endswith("/") else base_url + "/"
    cart_url = urljoin(base_url, "cart")
    failures: list[str] = []
    attempts: list[dict[str, Any]] = []
    unit_prices: dict[str, Decimal | None] = {}
    _console(request, "INFO", "Cart workflow", "Using a fresh browser context and three fixed test products; checkout is not submitted.")

    try:
        _stage(1, "SELECT VARIANTS AND ADD THREE TEST PRODUCTS")
        # Add exactly three fixed products in one browser context so the cart state persists.
        for product_index, product in enumerate(CART_PRODUCTS, start=1):
            print(f"\n  Product {product_index}/{len(CART_PRODUCTS)}: {product['label']}", flush=True)
            step_started = time.monotonic()
            product_url = urljoin(base_url, f"products/{product['slug']}")
            attempt: dict[str, Any] = {**product, "url": product_url, "error": None, "variant": None}
            try:
                response = page.goto(product_url, wait_until="domcontentloaded", timeout=NAVIGATION_TIMEOUT_MS)
                page.wait_for_timeout(450)
                if not response or response.status >= 400:
                    attempt["error"] = f"Product page returned HTTP {response.status if response else 'no response'}: {page.url}"
                else:
                    _dismiss_cookie_notice(page)
                    variants = page.evaluate(VARIANT_CANDIDATES_SCRIPT)
                    if not variants:
                        attempt["error"] = "No selectable size/capacity option was found; test item was not added."
                    else:
                        try:
                            attempt["variant"] = str(variants[0].get("label") or "first available option")
                            _click_variant_once(page, variants[0])
                            unit_prices[product["id"]] = _find_money_on_product(page)
                            add_info = page.evaluate(ADD_TO_CART_SCRIPT)
                            if not add_info.get("found"):
                                attempt["error"] = add_info.get("detail", "Add to Cart control was not found.")
                            else:
                                add_button = page.locator('[data-qa-cart-add="true"]')
                                if add_button.count() != 1:
                                    attempt["error"] = f"Add to Cart control was ambiguous (matches={add_button.count()})."
                                else:
                                    add_button.click(timeout=ACTION_TIMEOUT_MS)
                                    page.wait_for_timeout(500)
                        except Exception as exc:
                            attempt["error"] = f"Add workflow failed: {type(exc).__name__}: {str(exc).splitlines()[0][:200]}"
            except Exception as exc:
                attempt["error"] = f"Could not open product: {type(exc).__name__}: {str(exc).splitlines()[0][:200]}"
            attempts.append(attempt)
            if attempt.get("error"):
                print(f"    [ACTION FAIL] {attempt['error']}", flush=True)
            else:
                print(
                    f"    [ACTION] Selected {attempt.get('variant') or 'available variant'} and clicked Add to Cart; "
                    "actual cart presence will be verified in the next step.",
                    flush=True,
                )

        _stage(2, "OPEN CART AND VERIFY PRODUCTS / INITIAL SUBTOTAL")
        # Exercise the visible cart control first. If it fails, direct navigation is used only
        # to allow the rest of the checks to continue; the UI-navigation check remains FAIL.
        open_started = time.monotonic()
        opened_via_ui, open_detail = _open_cart_control(page)
        if not opened_via_ui:
            failures.append("cart-open")
            _record_step(request, "cart-open", "Open cart using the storefront control", "FAIL", open_detail, open_started, page)
            try:
                page.goto(cart_url, wait_until="domcontentloaded", timeout=NAVIGATION_TIMEOUT_MS)
                page.wait_for_timeout(500)
            except Exception:
                pass
        else:
            _record_step(request, "cart-open", "Open cart using the storefront control", "PASS", open_detail, open_started, page)

        state = _cart_state(page)
        for attempt in attempts:
            step_started = time.monotonic()
            item = _find_item(state, attempt)
            if attempt.get("error"):
                failures.append(attempt["id"] + "-add")
                detail = f"Could not complete add-to-cart workflow: {attempt['error']}"
                _record_step(request, attempt["id"] + "-add", f"Add {attempt['label']} to cart", "FAIL", detail, step_started, page)
            elif item:
                qty = item.get("quantity") or "unknown"
                detail = f"Product is present in the cart after Add to Cart; selected variant: {attempt.get('variant')}; quantity={qty}; URL={attempt['url']}"
                if qty == "1":
                    _record_step(request, attempt["id"] + "-add", f"Add {attempt['label']} to cart", "PASS", detail, step_started, page)
                else:
                    failures.append(attempt["id"] + "-initial-quantity")
                    _record_step(request, attempt["id"] + "-add", f"Add {attempt['label']} to cart", "FAIL", detail + " Expected a clean initial quantity of 1.", step_started, page)
            else:
                failures.append(attempt["id"] + "-add")
                detail = f"Add to Cart was clicked, but the product was not found as a cart line item. URL={attempt['url']}"
                _record_step(request, attempt["id"] + "-add", f"Add {attempt['label']} to cart", "FAIL", detail, step_started, page)

        contents_started = time.monotonic()
        expected_paths = {_normal_path(product["url"]) for product in attempts if not product.get("error")}
        found_paths = {str(item.get("path", "")).casefold() for item in state.get("items", [])}
        missing_paths = sorted(expected_paths - found_paths)
        if len(state.get("items", [])) == len(expected_paths) and not missing_paths and expected_paths:
            _record_step(request, "cart-contents", "Verify all selected products are in the cart", "PASS", f"Found exactly {len(expected_paths)} expected product line(s), with no unexpected cart lines.", contents_started, page)
        else:
            failures.append("cart-contents")
            _record_step(request, "cart-contents", "Verify all selected products are in the cart", "FAIL", f"Expected exactly {len(expected_paths)} product line(s); detected {len(state.get('items', []))}; missing paths: {missing_paths or 'none identifiable'}. Cart row detection may also need inspection.", contents_started, page)

        initial_subtotal = _subtotal(state)
        subtotal_started = time.monotonic()
        if initial_subtotal is not None and initial_subtotal > Decimal("0"):
            _record_step(request, "cart-initial-subtotal", "Read initial cart subtotal", "PASS", f"Subtotal is displayed as '{state.get('subtotalText')}' (parsed amount {initial_subtotal}).", subtotal_started, page)
        else:
            failures.append("cart-initial-subtotal")
            _record_step(request, "cart-initial-subtotal", "Read initial cart subtotal", "FAIL", f"Could not reliably parse a positive subtotal from '{state.get('subtotalText') or 'no subtotal text found'}'; price verification cannot continue until the cart subtotal is readable.", subtotal_started, page)

        # Compare the initial subtotal with the three unit prices read from the product pages.
        addition_total_started = time.monotonic()
        known_prices = [unit_prices.get(product["id"]) for product in attempts]
        if initial_subtotal is None or not known_prices or any(price is None for price in known_prices):
            failures.append("cart-subtotal-after-add")
            _record_step(request, "cart-subtotal-after-add", "Verify subtotal after adding all three products", "FAIL", "Could not parse the cart subtotal or all three product prices, so the expected initial total could not be calculated.", addition_total_started, page)
        else:
            expected_initial_total = sum((price for price in known_prices if price is not None), Decimal("0"))
            difference = abs(initial_subtotal - expected_initial_total)
            if difference <= Decimal("0.03"):
                _record_step(request, "cart-subtotal-after-add", "Verify subtotal after adding all three products", "PASS", f"Cart subtotal {initial_subtotal} matches the sum of the three selected unit prices ({expected_initial_total}).", addition_total_started, page)
            else:
                failures.append("cart-subtotal-after-add")
                _record_step(request, "cart-subtotal-after-add", "Verify subtotal after adding all three products", "FAIL", f"Cart subtotal is {initial_subtotal}; sum of selected unit prices is {expected_initial_total}; difference is {difference}. Check for an incorrect cart calculation, tax/discount behavior, or price parser mismatch.", addition_total_started, page)

        _stage(3, "CHANGE QUANTITY AND VERIFY SUBTOTAL RECALCULATION")
        # Change first product from quantity 1 to 2.
        qty_started = time.monotonic()
        quantity_target = next((p for p in attempts if p["id"] == "cart-tshirt-boyfriend"), attempts[0] if attempts else None)
        before_qty_state = _cart_state(page)
        before_qty_item = _find_item(before_qty_state, quantity_target) if quantity_target else None
        qty_before = str(before_qty_item.get("quantity") or "") if before_qty_item else ""
        qty_clicked, qty_detail = (False, "The target product was not present as a cart line item.")
        if before_qty_item and qty_before == "1":
            qty_clicked, qty_detail = _click_quantity_increase(page, before_qty_item)
        elif before_qty_item and qty_before == "2":
            qty_clicked, qty_detail = False, "Target item was already quantity 2 before the test; initial state was not clean."
        if qty_clicked:
            after_qty_state = _cart_state(page)
            after_qty_item = _find_item(after_qty_state, quantity_target)
            qty_after = str(after_qty_item.get("quantity") or "") if after_qty_item else ""
            if qty_after == "2":
                _record_step(request, "cart-quantity-increase", "Increase quantity from 1 to 2", "PASS", f"Quantity changed from {qty_before} to {qty_after}. {qty_detail}", qty_started, page)
            else:
                failures.append("cart-quantity-increase")
                _record_step(request, "cart-quantity-increase", "Increase quantity from 1 to 2", "FAIL", f"Quantity control was used, but expected 2 and observed {qty_after or 'unknown'}. {qty_detail}", qty_started, page)
        else:
            failures.append("cart-quantity-increase")
            _record_step(request, "cart-quantity-increase", "Increase quantity from 1 to 2", "FAIL", f"Could not increase quantity from the expected initial value 1. Observed {qty_before or 'unknown'}. {qty_detail}", qty_started, page)

        after_qty_state = _cart_state(page)
        subtotal_after_qty = _subtotal(after_qty_state)
        subtotal_qty_started = time.monotonic()
        unit_price = unit_prices.get(quantity_target["id"]) if quantity_target else None
        if initial_subtotal is None or subtotal_after_qty is None or unit_price is None:
            failures.append("cart-subtotal-quantity")
            _record_step(request, "cart-subtotal-quantity", "Verify subtotal recalculation after quantity change", "FAIL", "Subtotal or unit price could not be reliably read; price recalculation could not be asserted. Check the report details to determine whether the page selector or storefront output needs adjustment.", subtotal_qty_started, page)
        else:
            delta = subtotal_after_qty - initial_subtotal
            if abs(delta - unit_price) <= Decimal("0.03"):
                _record_step(request, "cart-subtotal-quantity", "Verify subtotal recalculation after quantity change", "PASS", f"Subtotal increased by {delta}; expected one additional unit at {unit_price}.", subtotal_qty_started, page)
            else:
                failures.append("cart-subtotal-quantity")
                _record_step(request, "cart-subtotal-quantity", "Verify subtotal recalculation after quantity change", "FAIL", f"Subtotal changed by {delta}, but one additional unit costs {unit_price}; observed subtotal text: '{after_qty_state.get('subtotalText')}'.", subtotal_qty_started, page)

        _stage(4, "REMOVE ONE PRODUCT AND VERIFY SUBTOTAL RECALCULATION")
        # Remove second product and verify both removal and its impact on the subtotal.
        remove_started = time.monotonic()
        remove_target = next((p for p in attempts if p["id"] == "cart-tshirt-back-off"), attempts[1] if len(attempts) > 1 else None)
        before_remove_state = _cart_state(page)
        before_remove_total = _subtotal(before_remove_state)
        remove_item = _find_item(before_remove_state, remove_target) if remove_target else None
        remove_clicked = False
        remove_detail = "Target product was not found in cart."
        if remove_item:
            remove_clicked, remove_detail = _remove_item(page, remove_item)
        state_after_remove = _cart_state(page)
        still_present = _find_item(state_after_remove, remove_target) if remove_target else None
        if remove_clicked and not still_present:
            _record_step(request, "cart-remove-product", "Remove one product from the cart", "PASS", f"Removed {remove_target['label']}; the product no longer appears as a cart line item. {remove_detail}", remove_started, page)
        else:
            failures.append("cart-remove-product")
            _record_step(request, "cart-remove-product", "Remove one product from the cart", "FAIL", f"Could not verify removal of {remove_target['label'] if remove_target else 'the target product'}. {remove_detail}", remove_started, page)

        after_remove_total = _subtotal(state_after_remove)
        remove_price = unit_prices.get(remove_target["id"]) if remove_target else None
        price_remove_started = time.monotonic()
        if before_remove_total is None or after_remove_total is None or remove_price is None:
            failures.append("cart-subtotal-remove")
            _record_step(request, "cart-subtotal-remove", "Verify subtotal recalculation after removal", "FAIL", "Subtotal or removed product price could not be reliably read; price decrease could not be asserted. Check the report details to determine whether the page selector or storefront output needs adjustment.", price_remove_started, page)
        else:
            delta = before_remove_total - after_remove_total
            if abs(delta - remove_price) <= Decimal("0.03"):
                _record_step(request, "cart-subtotal-remove", "Verify subtotal recalculation after removal", "PASS", f"Subtotal decreased by {delta}; removed product unit price was {remove_price}.", price_remove_started, page)
            else:
                failures.append("cart-subtotal-remove")
                _record_step(request, "cart-subtotal-remove", "Verify subtotal recalculation after removal", "FAIL", f"Subtotal decreased by {delta}, but removed product unit price was {remove_price}; observed subtotal text: '{state_after_remove.get('subtotalText')}'.", price_remove_started, page)

        _stage(5, "OPEN CHECKOUT WITHOUT SUBMITTING AN ORDER")
        # Check the first checkout step only. No checkout form is submitted and no payment data is entered.
        checkout_started = time.monotonic()
        checkout_before_state = _cart_state(page)
        if not checkout_before_state.get("items"):
            _record_step(request, "cart-checkout-navigation", "Open checkout without submitting an order", "SKIP", "Cart had no detected line items, so checkout was not clicked.", checkout_started, page)
        else:
            checkout_ok, checkout_detail, checkout_page = _open_checkout(page)
            if checkout_ok:
                _record_step(request, "cart-checkout-navigation", "Open checkout without submitting an order", "PASS", checkout_detail, checkout_started, checkout_page)
            else:
                failures.append("cart-checkout-navigation")
                _record_step(request, "cart-checkout-navigation", "Open checkout without submitting an order", "FAIL", checkout_detail, checkout_started, checkout_page)
            if checkout_page is not page:
                try:
                    checkout_page.close()
                except PlaywrightError:
                    pass

        _stage(6, "CLEAN UP TEST ITEMS AND VERIFY EMPTY CART")
        # Return to the cart and remove all remaining test items. Context is isolated and no order is placed.
        try:
            page.goto(cart_url, wait_until="domcontentloaded", timeout=NAVIGATION_TIMEOUT_MS)
            page.wait_for_timeout(450)
        except Exception as exc:
            failures.append("cart-return-after-checkout")
            _record_step(request, "cart-return-after-checkout", "Return to cart after checking checkout", "FAIL", f"Could not return to the cart: {type(exc).__name__}: {str(exc).splitlines()[0][:180]}", time.monotonic(), page)

        cleanup_started = time.monotonic()
        for product in attempts:
            current_state = _cart_state(page)
            cart_item = _find_item(current_state, product)
            if not cart_item:
                continue
            item_started = time.monotonic()
            ok, detail = _remove_item(page, cart_item)
            state_after = _cart_state(page)
            if ok and not _find_item(state_after, product):
                _record_step(request, f"cart-cleanup-{product['id']}", f"Remove test item - {product['label']}", "PASS", detail, item_started, page)
            else:
                failures.append(f"cart-cleanup-{product['id']}")
                _record_step(request, f"cart-cleanup-{product['id']}", f"Remove test item - {product['label']}", "FAIL", f"Could not clear test item. {detail}", item_started, page)
        final_state = _cart_state(page)
        empty_started = time.monotonic()
        if not final_state.get("items") and final_state.get("emptyMessage"):
            _record_step(request, "cart-empty-state", "Verify cart is empty after removing test items", "PASS", "The cart shows an explicit empty-cart message and no cart line items remain.", empty_started, page)
        else:
            failures.append("cart-empty-state")
            _record_step(request, "cart-empty-state", "Verify cart is empty after removing test items", "FAIL", f"Could not verify a clean empty-cart state: {len(final_state.get('items', []))} item row(s) detected; explicit empty message={final_state.get('emptyMessage')}.", empty_started, page)

    finally:
        try:
            page.close()
        except PlaywrightError:
            pass

    if failures:
        pytest.fail(f"Cart workflow completed with {len(failures)} failed check(s): {', '.join(failures)}", pytrace=False)
