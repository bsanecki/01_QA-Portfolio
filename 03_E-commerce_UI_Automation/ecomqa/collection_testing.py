"""Discovery helpers for Section 02 (T-shirts) and Section 03 (mugs)."""
from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit
from typing import Any

from playwright.sync_api import sync_playwright

from config import DISCOVERY_WAIT_MS, VIEWPORT
from ecomqa.browser import launch_chromium

SECTION_CONFIGS: dict[str, dict[str, str]] = {
    "tshirts": {
        "section_title": "Section 02 - T-shirt Collection",
        "collection_path": "collections/panda-shirts",
        "test_file": "test_02_tshirt_collection.py",
        "scope": (
            "Open the T-shirt collection, open each product from its collection card, and click "
            "each available size option. No product-gallery images are clicked. No items are added "
            "to the cart and no checkout is submitted."
        ),
        "expects_sizes": "true",
    },
    "mugs": {
        "section_title": "Section 03 - Mug Collection",
        "collection_path": "collections/panda-mugs",
        "test_file": "test_03_mug_collection.py",
        "scope": (
            "Open the mug collection, open each product from its collection card, and click each "
            "available size or capacity option. No product-gallery images are clicked. A mug with "
            "no selectable size/capacity option is reported as SKIP for that sub-check. No items "
            "are added to the cart and no checkout is submitted."
        ),
        "expects_sizes": "false",
    },
}


PRODUCT_LINKS_SCRIPT = r"""() => {
  const visible = (el) => {
    if (!el) return false;
    const style = getComputedStyle(el);
    const rect = el.getBoundingClientRect();
    return style.display !== 'none' && style.visibility !== 'hidden' &&
      Number(style.opacity || 1) > 0 && rect.width > 0 && rect.height > 0;
  };
  const normalPath = (value) => {
    try {
      const url = new URL(value, location.href);
      return url.origin + url.pathname.replace(/\/$/, '');
    } catch (_) { return ''; }
  };
  const unique = new Map();
  for (const a of document.querySelectorAll('a[href*="/products/"]')) {
    if (!visible(a)) continue;
    const href = normalPath(a.href);
    if (!href || !/\/products\//i.test(href)) continue;
    let card = a.closest('article, li, [data-testid*="product"], [class*="product-card"], [class*="ProductCard"]');
    if (!card) {
      card = a;
      for (let i = 0; i < 4 && card.parentElement; i++) {
        const parent = card.parentElement;
        if (parent.querySelector('img') || parent.querySelector('h2,h3,h4')) card = parent;
      }
    }
    const titleNode = card.querySelector('h2,h3,h4,[class*="product-title"],[class*="product-name"],[class*="ProductTitle"]');
    const image = a.querySelector('img') || card.querySelector('img');
    const label = (titleNode?.innerText || a.getAttribute('aria-label') || image?.alt || a.innerText || '')
      .replace(/\s+/g, ' ').trim();
    const old = unique.get(href);
    if (!old || label.length > old.label.length) unique.set(href, {url: href, path: new URL(href).pathname, label: label || new URL(href).pathname.split('/').pop()});
  }
  return [...unique.values()].filter(item => item.path.toLowerCase().includes('/products/'));
}"""

VARIANT_CANDIDATES_SCRIPT = r"""() => {
  const root = document.querySelector('main') || document.body;
  const visible = (el) => {
    if (!el) return false;
    const style = getComputedStyle(el);
    const rect = el.getBoundingClientRect();
    return style.display !== 'none' && style.visibility !== 'hidden' &&
      Number(style.opacity || 1) > 0 && rect.width > 0 && rect.height > 0;
  };
  const norm = (value) => String(value || '').replace(/\s+/g, ' ').trim();
  const sizeLike = (value) => /^(?:xxxs|xxs|xs|s|m|l|xl|xxl|xxxl|xxxxl|xxxxxl|[2-6]xl|[2-6]x|extra\s?small|small|medium|large|extra\s?large|one\s?size|unisex\s?xs|unisex\s?s|unisex\s?m|unisex\s?l|unisex\s?xl|adult\s?(?:xs|s|m|l|xl|xxl)|(?:[1-9]\d?)(?:\s?oz|\s?ounce(?:s)?|\s?ml|\s?cl|\s?fl\s?oz|\s?inch(?:es)?|\s?in))$/i.test(norm(value));
  const groupFor = (el) => {
    const aria = el.getAttribute('aria-label');
    if (aria && /size|capacity|volume|variant|product type/i.test(aria)) return norm(aria);
    const name = el.getAttribute('name');
    if (name && /size|capacity|volume/i.test(name)) return norm(name);
    const fieldset = el.closest('fieldset');
    if (fieldset) {
      const legend = fieldset.querySelector('legend');
      if (legend && norm(legend.innerText)) return norm(legend.innerText);
    }
    for (let parent = el.parentElement, depth = 0; parent && parent !== root && depth < 5; parent = parent.parentElement, depth++) {
      const cls = String(parent.className || '');
      const ariaParent = parent.getAttribute('aria-label');
      if (/size|capacity|volume|variant/i.test(cls) && parent.children.length < 20) {
        const heading = parent.querySelector(':scope > label,:scope > legend,:scope > h2,:scope > h3,:scope > h4,[data-option-name]');
        const text = norm(heading?.innerText || ariaParent || parent.getAttribute('data-option-name') || '');
        if (text && text.length < 90) return text;
        if (/size|capacity|volume/i.test(cls)) return cls.replace(/[-_]+/g, ' ').slice(0, 80);
      }
      const label = parent.querySelector(':scope > label,:scope > legend,:scope > h2,:scope > h3,:scope > h4');
      if (label && norm(label.innerText).length < 60 && /size|capacity|volume/i.test(label.innerText)) return norm(label.innerText);
    }
    return norm(name || '');
  };
  const goodOption = (label, group) => {
    const text = norm(label);
    // Do not mistake help links such as "Size guide" for selectable variants.
    if (!text || /size\s*(?:guide|chart|table)|fit\s*guide|measurements|how\s+to\s+measure|help\s+with\s+sizing/i.test(text)) return false;
    if (/^(select|choose|please select|select a size|choose a size|size)$/i.test(text)) return false;
    // Only actual size/capacity-shaped labels qualify. A parent whose class contains
    // "size" is not sufficient: that was incorrectly admitting the "Size guide" link.
    return sizeLike(text);
  };
  const output = [];
  let selectIndex = 0;
  for (const select of root.querySelectorAll('select')) {
    if (!visible(select) || select.disabled) continue;
    const group = groupFor(select);
    const options = [...select.options].filter(option => !option.disabled && option.value && goodOption(option.textContent, group));
    if (!options.length) continue;
    select.setAttribute('data-qa-variant-select-index', String(selectIndex));
    for (const option of options) {
      output.push({type: 'select', label: norm(option.textContent), group, value: option.value, selectIndex, controlIndex: -1});
    }
    selectIndex++;
  }

  const controls = [];
  for (const input of root.querySelectorAll('input[type="radio"]')) {
    const labelEl = input.labels && input.labels.length ? input.labels[0] : null;
    const target = labelEl && visible(labelEl) ? labelEl : (visible(input) ? input : null);
    if (!target || input.disabled) continue;
    const label = norm(labelEl?.innerText || input.getAttribute('aria-label') || input.value);
    const group = groupFor(input);
    if (!goodOption(label, group)) continue;
    controls.push({target, input, item: {type: 'control', controlType: 'radio', label, group, value: input.value, controlIndex: -1}});
  }
  for (const el of root.querySelectorAll('button,[role="radio"],[role="option"],[role="button"],[data-value]')) {
    if (!visible(el) || el.disabled || el.getAttribute('aria-disabled') === 'true') continue;
    if (el.matches('button') && /add to cart|buy now|checkout|quantity|minus|plus|previous|next|zoom|share/i.test((el.innerText || '') + ' ' + (el.getAttribute('aria-label') || ''))) continue;
    if (el.querySelector('input[type="radio"]')) continue;
    const label = norm(el.innerText || el.getAttribute('aria-label') || el.getAttribute('title') || el.getAttribute('data-value'));
    if (!label || label.length > 45) continue;
    const group = groupFor(el);
    if (!goodOption(label, group)) continue;
    controls.push({target: el, input: null, item: {type: 'control', controlType: 'button', label, group, value: el.getAttribute('data-value') || '', controlIndex: -1}});
  }
  const seen = new Set();
  const uniqueControls = [];
  for (const entry of controls) {
    const key = [entry.item.group.toLowerCase(), entry.item.label.toLowerCase() ].join('|');
    if (seen.has(key)) continue;
    seen.add(key);
    uniqueControls.push(entry);
  }
  uniqueControls.forEach((entry, index) => {
    entry.item.controlIndex = index;
    entry.target.setAttribute('data-qa-variant-index', String(index));
  });
  output.push(...uniqueControls.map(entry => entry.item));
  return output;
}"""


def _clean_url(value: str) -> str:
    parts = urlsplit(value)
    return urlunsplit((parts.scheme, parts.netloc, parts.path.rstrip("/"), "", ""))


def _normalize_product_title(value: str) -> str:
    """Normalize a card title for duplicate-listing detection."""
    text = (value or "").casefold()
    text = re.sub(r"\bproduct image\s*\(\s*\d+\s*\)", " ", text)
    text = re.sub(r"\b\d+(?:[.,]\d{2})?\s*(?:zł|pln|eur|usd|gbp|cad|aud|nzd|sek|nok|dkk|inr|jpy|myr|sgd|mxn|brl|chf)\b", " ", text)
    text = re.sub(r"\bplus tax\b", " ", text)
    return re.sub(r"[^a-z0-9]+", " ", text).strip()




def _prepare_product_inventory(products: list[dict[str, Any]]) -> tuple[list[dict[str, str]], list[dict[str, str]], int]:
    """Deduplicate URL aliases, but preserve distinct product URLs even when titles repeat.

    A numeric slug suffix (for example ``-2``) can represent a distinct product design.
    When such a URL reuses the same visible title, record a catalogue-title issue but do
    not remove the product from the test inventory.
    """
    raw_items = sorted(products, key=lambda item: _clean_url(item.get("url", "")).casefold())
    seen_paths: set[str] = set()
    seen_product_identity: dict[tuple[str, str], dict[str, str]] = {}
    clean_products: list[dict[str, str]] = []
    repeated_titles: list[dict[str, str]] = []

    for item in raw_items:
        url = _clean_url(item.get("url", ""))
        path = urlsplit(url).path.rstrip("/")
        path_key = path.casefold()
        if "/products/" not in path.lower() or path_key in seen_paths:
            continue
        seen_paths.add(path_key)
        label = (item.get("label") or path.rsplit("/", 1)[-1]).strip()
        slug = path.rsplit("/", 1)[-1].casefold()
        slug_base = re.sub(r"-\d+$", "", slug)
        title_key = _normalize_product_title(label)
        product = {"url": url, "path": path, "label": label}
        identity = (title_key, slug_base)
        previous = seen_product_identity.get(identity) if title_key else None
        if previous:
            repeated_titles.append({
                "title": label,
                "primary_url": previous["url"],
                "duplicate_url": url,
            })
        elif title_key:
            seen_product_identity[identity] = product
        # Crucial: every distinct product path remains in the sweep, including -2 slugs.
        clean_products.append(product)

    return clean_products, repeated_titles, len(seen_paths)

def _safe_id(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]+", "-", value).strip("-").lower()[:72] or "product"


def _make_spec(section_key: str, collection_url: str, product: dict[str, Any], kind: str, **extra: Any) -> dict[str, Any]:
    section = SECTION_CONFIGS[section_key]
    product_id = _safe_id(urlsplit(product["url"]).path.rsplit("/", 1)[-1])
    return {
        "id": f"{section_key}-{product_id}-{kind}-{extra.get('index', '')}".strip("-"),
        "kind": kind,
        "sectionKey": section_key,
        "label": extra.pop("caseLabel", product.get("label") or product_id),
        "collectionUrl": collection_url,
        "productUrl": product["url"],
        "productPath": urlsplit(product["url"]).path,
        "productLabel": product.get("label") or product_id,
        "discovered": True,
        "expectsSizes": section["expects_sizes"] == "true",
        **extra,
    }


def discover_collection_section(
    base_url: str,
    section_key: str,
    headless: bool,
    slowmo: int,
    report_dir: Path,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Discover collection products and their selectable size options only."""
    if section_key not in SECTION_CONFIGS:
        raise ValueError(f"Unknown collection section: {section_key}")
    section = SECTION_CONFIGS[section_key]
    collection_url = urljoin(base_url if base_url.endswith("/") else base_url + "/", section["collection_path"])
    discovery: dict[str, Any] = {
        "section_key": section_key,
        "section_title": section["section_title"],
        "collection_url": collection_url,
        "collection": {"ok": False, "status": None, "url": collection_url, "details": "Collection discovery did not complete."},
        "products_discovered": 0,
        "product_cards_found": 0,
        "duplicate_product_listings": [],
        "variant_options_discovered": None,
        "variant_options_discovered_during_product_tests": True,
        "section_screenshot": None,
        "discovery_error": None,
        "products": [],
    }
    specs: list[dict[str, Any]] = []
    try:
        with sync_playwright() as playwright:
            browser = launch_chromium(playwright, headless=headless, slow_mo=slowmo)
            context = browser.new_context(viewport=VIEWPORT, accept_downloads=True, reduced_motion="reduce")
            page = context.new_page()
            page.set_default_navigation_timeout(15_000)
            try:
                response = page.goto(collection_url, wait_until="domcontentloaded", timeout=15_000)
                page.wait_for_timeout(DISCOVERY_WAIT_MS)
                status = response.status if response else None
                discovery["collection"] = {
                    "ok": bool(response and status is not None and status < 400),
                    "status": status,
                    "url": page.url,
                    "details": f"Collection page response: HTTP {status if status is not None else 'no response'}; URL={page.url}",
                }
                if response and status is not None and status < 400:
                    # A bounded scroll allows lazy-loaded collection cards to enter the DOM without
                    # creating an unbounded scroll loop on stores with infinite scrolling.
                    previous_height = -1
                    stable_rounds = 0
                    for _ in range(5):
                        height = page.evaluate("document.documentElement.scrollHeight")
                        if height == previous_height:
                            stable_rounds += 1
                        else:
                            stable_rounds = 0
                        if stable_rounds >= 2:
                            break
                        previous_height = height
                        page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)")
                        page.wait_for_timeout(180)
                    page.evaluate("window.scrollTo(0, 0)")
                    page.wait_for_timeout(120)
                    products = page.evaluate(PRODUCT_LINKS_SCRIPT)
                    # Keep every distinct product URL. Repeated-title/suffixed-slug patterns
                    # are recorded separately and do not remove products from variant testing.
                    clean_products, duplicate_listings, unique_path_count = _prepare_product_inventory(products)
                    discovery["product_cards_found"] = unique_path_count
                    discovery["duplicate_product_listings"] = duplicate_listings
                    discovery["products"] = clean_products
                    discovery["products_discovered"] = len(clean_products)
                    try:
                        screenshot = report_dir / "collection-preview.png"
                        page.screenshot(path=str(screenshot), full_page=True, timeout=8_000)
                        discovery["section_screenshot"] = screenshot.name
                    except Exception as exc:
                        discovery["collection_screenshot_error"] = f"{type(exc).__name__}: {str(exc).splitlines()[0][:160]}"

                    specs.append({
                        "id": f"{section_key}-collection-page-load",
                        "kind": "collection_page_load",
                        "sectionKey": section_key,
                        "label": f"Open {section['section_title']}",
                        "collectionUrl": collection_url,
                        "discovered": True,
                    })
                    if not clean_products:
                        specs.append({
                            "id": f"{section_key}-collection-discovery",
                            "kind": "setup_error",
                            "sectionKey": section_key,
                            "label": f"{section['section_title']} - discover product cards",
                            "discovered": False,
                            "discoveryNote": "The collection returned HTTP success, but no product cards could be discovered. This is a collection-page/discovery failure and must be investigated.",
                            "collectionUrl": collection_url,
                        })
                    else:
                        # Do not open product pages during discovery. Each product is opened exactly
                        # once by its runtime test; that test discovers and clicks all size options
                        # before moving on to the next product.
                        for product in clean_products:
                            specs.append(_make_spec(
                                section_key, collection_url, product, "product_size_sweep",
                                index="sizes",
                                caseLabel=f"Open product once and click all available sizes - {product['label']}",
                            ))
                        for duplicate_index, duplicate in enumerate(duplicate_listings, 1):
                            duplicate_key = _safe_id(duplicate["title"])
                            specs.append({
                                "id": f"{section_key}-duplicate-listing-{duplicate_index:02d}-{duplicate_key}",
                                "kind": "duplicate_product_title",
                                "sectionKey": section_key,
                                "label": f"Potential repeated product title - {duplicate['title']}",
                                "discovered": True,
                                "collectionUrl": collection_url,
                                "discoveryNote": (
                                    f"Two distinct product URLs appear to use the same visible title and an auto-suffixed slug. "
                                    f"This may be a catalogue-title defect rather than a duplicate product: both product URLs "
                                    f"remain in the test inventory and both receive their own size/capacity sweep. "
                                    f"Review the displayed title and product image. First URL: {duplicate['primary_url']}; "
                                    f"second URL: {duplicate['duplicate_url']}."
                                ),
                            })

                else:
                    specs.append({
                        "id": f"{section_key}-collection-page",
                        "kind": "setup_error",
                        "sectionKey": section_key,
                        "label": f"Open {section['section_title']}",
                        "discovered": False,
                        "discoveryNote": discovery["collection"]["details"],
                        "collectionUrl": collection_url,
                    })
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
        if not specs:
            specs.append({
                "id": f"{section_key}-discovery-error",
                "kind": "setup_error",
                "sectionKey": section_key,
                "label": f"Discover {section['section_title']}",
                "discovered": False,
                "discoveryNote": discovery["discovery_error"],
                "collectionUrl": collection_url,
            })
    return specs, discovery
