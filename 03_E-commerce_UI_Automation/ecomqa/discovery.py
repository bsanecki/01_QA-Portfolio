"""Homepage element and currency discovery for Section 01."""
from __future__ import annotations

import re
from urllib.parse import urlsplit
from typing import Any

from config import EXPECTED_PRODUCTS

CURRENCY_CODES = (
    "PLN EUR USD GBP CAD AUD CHF SEK NOK DKK CZK HUF RON BGN JPY CNY INR BRL MXN "
    "NZD SGD HKD TRY AED ZAR KRW ISK UAH ILS THB PHP MYR IDR VND ARS CLP COP SAR "
    "QAR KWD OMR TWD PKR BDT EGP NGN KES GHS GEL AMD AZN BAM RSD ALL MKD MDL UYU PEN"
).split()
CURRENCY_PATTERN = r"(?:" + "|".join(CURRENCY_CODES) + r")"

VISIBLE_LINKS_SCRIPT = r"""() => {
  const norm = (v) => String(v || '').replace(/\s+/g, ' ').trim();
  const visible = (el) => {
    if (!el || !el.isConnected || el.closest('[aria-hidden="true"], [inert]')) return false;
    const s = getComputedStyle(el), r = el.getBoundingClientRect();
    return s.display !== 'none' && s.visibility !== 'hidden' && Number(s.opacity) !== 0 && r.width > 0 && r.height > 0 && el.getClientRects().length > 0;
  };
  const label = (el) => norm(el.innerText || el.value || el.getAttribute('aria-label') || el.getAttribute('title') ||
    (el.querySelector('img') && el.querySelector('img').alt) || '');
  const nodes = Array.from(document.querySelectorAll('a[href]')).filter(visible);
  return nodes.map((el, index) => {
    let context = el;
    for (let n = 0; n < 4 && context.parentElement; n++) {
      context = context.parentElement;
      const txt = norm(context.innerText);
      if (txt.length >= 30 && txt.length <= 1000) break;
    }
    const r = el.getBoundingClientRect();
    return {
      index, tag: el.tagName.toLowerCase(), label: label(el), text: norm(el.innerText),
      ariaLabel: norm(el.getAttribute('aria-label')), title: norm(el.getAttribute('title')),
      href: el.href || '', path: (() => { try { return new URL(el.href, location.href).pathname; } catch(e) { return ''; } })(),
      target: norm(el.getAttribute('target')), className: typeof el.className === 'string' ? norm(el.className) : '',
      top: Math.round(r.top + window.scrollY), context: norm(context.innerText).slice(0, 900)
    };
  });
}"""

CURRENCY_TRIGGER_SCRIPT = r"""() => {
  const norm = (v) => String(v || '').replace(/\s+/g, ' ').trim();
  const visible = (el) => {
    if (!el || !el.isConnected || el.closest('[aria-hidden="true"], [inert]')) return false;
    const s = getComputedStyle(el), r = el.getBoundingClientRect();
    return s.display !== 'none' && s.visibility !== 'hidden' && Number(s.opacity) !== 0 && r.width > 0 && r.height > 0 && el.getClientRects().length > 0;
  };
  const selector = 'button, a, select, summary, [role="button"], [aria-haspopup], [aria-expanded]';
  const nodes = Array.from(document.querySelectorAll(selector)).filter(visible);
  const codeRe = /\b(PLN|EUR|USD|GBP|CAD|AUD|CHF|SEK|NOK|DKK|CZK|HUF|RON|BGN|JPY|CNY|INR|BRL|MXN|NZD|SGD|HKD|TRY|AED|ZAR|KRW|ISK|UAH|ILS|THB|PHP|MYR|IDR|VND|ARS|CLP|COP|SAR|QAR|KWD|OMR|TWD|PKR|BDT|EGP|NGN|KES|GHS|GEL|AMD|AZN|BAM|RSD|ALL|MKD|MDL|UYU|PEN)\b/i;
  const rows = nodes.map((el, index) => {
    const text = norm(el.innerText || el.value || el.getAttribute('aria-label') || el.getAttribute('title'));
    const aria = norm(el.getAttribute('aria-label'));
    const title = norm(el.getAttribute('title'));
    const match = (text + ' ' + aria + ' ' + title + ' ' + norm(el.getAttribute('data-currency'))).match(codeRe);
    const r = el.getBoundingClientRect();
    const headerish = r.top < 180 && r.right > window.innerWidth * 0.45;
    const namedCurrency = /currency|region|country|locale|market/i.test(aria + ' ' + title + ' ' + norm(el.className));
    const exact = match && norm(text).toUpperCase() === match[1].toUpperCase();
    let score = 0;
    if (match) score += 10;
    if (headerish) score += 8;
    if (namedCurrency) score += 8;
    if (exact) score += 12;
    if (el.tagName.toLowerCase() === 'select') score += 8;
    if (/cart|basket|bag/i.test(text + ' ' + aria + ' ' + title)) score -= 15;
    return { el, index, text, ariaLabel: aria, title, href: el.href || '', tag: el.tagName.toLowerCase(), code: match ? match[1].toUpperCase() : '', score, headerish };
  }).filter(row => row.score >= 18).sort((a,b) => b.score - a.score);
  const best = rows[0];
  if (!best) return { found: false, candidates: rows.length };
  best.el.setAttribute('data-qa-currency-trigger', 'true');
  const options = best.el.tagName.toLowerCase() === 'select'
    ? Array.from(best.el.options).map(o => ({ text: norm(o.textContent), value: o.value, selected: o.selected })) : [];
  return { found: true, tag: best.tag, text: best.text, ariaLabel: best.ariaLabel, title: best.title,
    href: best.href, code: best.code, headerish: best.headerish, options, candidates: rows.length };
}"""

CURRENCY_OPTIONS_SCRIPT = r"""() => {
  const norm = (v) => String(v || '').replace(/\s+/g, ' ').trim();
  const visible = (el) => {
    if (!el || !el.isConnected || el.closest('[aria-hidden="true"], [inert]')) return false;
    const s = getComputedStyle(el), r = el.getBoundingClientRect();
    return s.display !== 'none' && s.visibility !== 'hidden' && Number(s.opacity) !== 0 && r.width > 0 && r.height > 0 && el.getClientRects().length > 0;
  };
  const codeRe = /\b(PLN|EUR|USD|GBP|CAD|AUD|CHF|SEK|NOK|DKK|CZK|HUF|RON|BGN|JPY|CNY|INR|BRL|MXN|NZD|SGD|HKD|TRY|AED|ZAR|KRW|ISK|UAH|ILS|THB|PHP|MYR|IDR|VND|ARS|CLP|COP|SAR|QAR|KWD|OMR|TWD|PKR|BDT|EGP|NGN|KES|GHS|GEL|AMD|AZN|BAM|RSD|ALL|MKD|MDL|UYU|PEN)\b/i;
  const rows = [];
  for (const select of Array.from(document.querySelectorAll('select')).filter(visible)) {
    for (const option of Array.from(select.options)) {
      const text = norm(option.textContent), value = norm(option.value);
      const match = (text + ' ' + value).match(codeRe);
      if (match) rows.push({ code: match[1].toUpperCase(), label: text || value, value, mode: 'select', tag: 'option', selected: option.selected });
    }
  }
  const candidates = Array.from(document.querySelectorAll('button, a, [role="option"], [role="menuitem"], [data-currency]')).filter(visible);
  for (const el of candidates) {
    if (el.hasAttribute('data-qa-currency-trigger')) continue;
    const text = norm(el.innerText || el.value || el.getAttribute('aria-label') || el.getAttribute('title'));
    const value = norm(el.getAttribute('data-currency') || el.getAttribute('value'));
    const match = (text + ' ' + value).match(codeRe);
    if (!match) continue;
    const r = el.getBoundingClientRect();
    if (r.top > document.documentElement.scrollHeight || r.width === 0 || r.height === 0) continue;
    rows.push({ code: match[1].toUpperCase(), label: text || value, value, mode: 'menu', tag: el.tagName.toLowerCase(),
      role: norm(el.getAttribute('role')), href: el.href || '', selected: el.getAttribute('aria-selected') === 'true' });
  }
  rows.sort((a,b) => {
    const pri = x => (x.mode === 'select' ? 0 : 1) + (x.label.length < 18 ? 0 : 2);
    return pri(a) - pri(b) || a.label.length - b.label.length;
  });
  const deduped = [], seen = new Set();
  for (const row of rows) {
    if (seen.has(row.code)) continue;
    seen.add(row.code); deduped.push(row);
  }
  return deduped;
}"""

FIND_TARGET_SCRIPT = r"""(spec) => {
  const norm = (v) => String(v || '').replace(/\s+/g, ' ').trim();
  const visible = (el) => {
    if (!el || !el.isConnected || el.closest('[aria-hidden="true"], [inert]')) return false;
    const s = getComputedStyle(el), r = el.getBoundingClientRect();
    return s.display !== 'none' && s.visibility !== 'hidden' && Number(s.opacity) !== 0 && r.width > 0 && r.height > 0 && el.getClientRects().length > 0;
  };
  const label = (el) => norm(el.innerText || el.value || el.getAttribute('aria-label') || el.getAttribute('title') ||
    (el.querySelector('img') && el.querySelector('img').alt) || '');
  const pathOf = (el) => { try { return new URL(el.href, location.href).pathname.replace(/\/$/, '') || '/'; } catch(e) { return ''; } };
  const anchors = Array.from(document.querySelectorAll('a[href]')).filter(visible);
  const controls = Array.from(document.querySelectorAll('button, select, summary, [role="button"], [aria-haspopup], [aria-expanded]')).filter(visible);
  const kind = spec.kind;
  let candidates = [];
  const pathNeedle = String(spec.hrefPath || '').replace(/\/$/, '');
  const normPath = p => String(p || '').replace(/\/$/, '') || '/';
  if (kind === 'home_navigation') {
    if (pathNeedle) candidates = anchors.filter(a => /^home$/i.test(label(a)) && normPath(pathOf(a)) === normPath(pathNeedle));
    if (!candidates.length) candidates = anchors.filter(a => /^home$/i.test(label(a)));
    candidates.sort((a,b) => (a.getBoundingClientRect().top - b.getBoundingClientRect().top));
  } else if (kind === 'cart_round_trip') {
    candidates = anchors.filter(a => /(?:^|\/)(?:cart|basket)(?:\/|$)/i.test(pathOf(a)) || /\b(cart|shopping bag|basket)\b/i.test(label(a) + ' ' + a.getAttribute('aria-label') + ' ' + a.title));
  } else if (kind === 'shop_collection') {
    candidates = anchors.filter(a => /shop\s+the\s+collection/i.test(label(a)) || /\/collections\/all\b/i.test(pathOf(a)));
    candidates.sort((a,b) => (/shop\s+the\s+collection/i.test(label(b)) ? 1 : 0) - (/shop\s+the\s+collection/i.test(label(a)) ? 1 : 0));
  } else if (kind === 'product') {
    const slug = String(spec.slug || '').toLowerCase();
    candidates = anchors.filter(a => pathOf(a).toLowerCase().includes('/products/') && pathOf(a).toLowerCase().includes(slug));
  } else if (kind === 'shirt_collection') {
    candidates = anchors.filter(a => /panda-shirts/i.test(pathOf(a)) || (/see\s+the\s+whole\s+collection/i.test(label(a)) && /shirt|tee|t-shirt/i.test((a.parentElement && a.parentElement.innerText) || '')));
  } else if (kind === 'mug_collection') {
    candidates = anchors.filter(a => /panda-mugs/i.test(pathOf(a)) || (/see\s+the\s+whole\s+collection/i.test(label(a)) && /mug|cup/i.test((a.parentElement && a.parentElement.innerText) || '')));
  } else if (kind === 'contact_cta' || kind === 'contact_footer') {
    if (pathNeedle) candidates = anchors.filter(a => normPath(pathOf(a)) === normPath(pathNeedle));
    if (!candidates.length) {
      candidates = anchors.filter(a => /^contact$/i.test(label(a)) || /\bcontact\b/i.test(a.getAttribute('aria-label') || ''));
      if (kind === 'contact_cta') candidates = candidates.filter(a => /button|btn|cta/i.test(String(a.className)) || a.getBoundingClientRect().top > window.innerHeight * 0.45);
      else candidates = candidates.filter(a => !/\/pages\/contact$/i.test(pathOf(a)));
    }
    candidates.sort((a,b) => a.getBoundingClientRect().top - b.getBoundingClientRect().top);
    if (kind === 'contact_footer') candidates = candidates.slice(-1);
    else candidates = candidates.slice(0, 1);
  } else if (kind === 'terms_of_service') {
    candidates = anchors.filter(a => /terms-of-service|terms of service/i.test(pathOf(a) + ' ' + label(a)));
  } else if (kind === 'privacy_policy') {
    candidates = anchors.filter(a => /privacy-policy|privacy policy/i.test(pathOf(a) + ' ' + label(a)));
  } else if (kind === 'returns_faq') {
    candidates = anchors.filter(a => /returns-faq|returns\s*(?:&|and)\s*faq|returns\s+faq/i.test(pathOf(a) + ' ' + label(a)));
  } else if (kind === 'currency_trigger') {
    const marker = document.querySelector('[data-qa-currency-trigger="true"]');
    if (marker && visible(marker)) candidates = [marker];
    else {
      const codeRe = /\b(PLN|EUR|USD|GBP|CAD|AUD|CHF|SEK|NOK|DKK|CZK|HUF|RON|BGN|JPY|CNY|INR|BRL|MXN|NZD|SGD|HKD|TRY|AED|ZAR|KRW|ISK|UAH|ILS|THB|PHP|MYR|IDR|VND|ARS|CLP|COP|SAR|QAR|KWD|OMR|TWD|PKR|BDT|EGP|NGN|KES|GHS|GEL|AMD|AZN|BAM|RSD|ALL|MKD|MDL|UYU|PEN)\b/i;
      candidates = controls.concat(anchors).filter(el => codeRe.test(label(el) + ' ' + (el.getAttribute('aria-label') || '') + ' ' + (el.getAttribute('title') || '')));
      candidates.sort((a,b) => {
        const score = el => { const r=el.getBoundingClientRect(), t=label(el); return (r.top < 180 ? 10 : 0) + (/^\w{3}$/.test(t) ? 10 : 0) + (/cart|basket|bag/i.test(t) ? -15 : 0); };
        return score(b)-score(a);
      });
    }
  } else if (kind === 'currency_option') {
    const code = String(spec.currencyCode || '').toUpperCase();
    const re = new RegExp('\\b' + code + '\\b', 'i');
    candidates = Array.from(document.querySelectorAll('button, a, [role="option"], [role="menuitem"]')).filter(visible)
      .filter(el => re.test(label(el) + ' ' + (el.getAttribute('data-currency') || '') + ' ' + (el.getAttribute('value') || '')));
    candidates.sort((a,b) => Math.abs(label(a).length - String(spec.currencyLabel || '').length) - Math.abs(label(b).length - String(spec.currencyLabel || '').length));
  }
  const el = candidates[0];
  if (!el) return { found: false, candidates: candidates.length };
  const targetId = String(spec.id || 'target').replace(/[^a-z0-9_-]/gi, '-');
  el.setAttribute('data-qa-target', targetId);
  return { found: true, count: candidates.length, tag: el.tagName.toLowerCase(), label: label(el),
    href: el.href || '', path: pathOf(el), disabled: Boolean(el.disabled) || el.getAttribute('aria-disabled') === 'true' };
}"""

CURRENT_CURRENCY_SCRIPT = r"""() => {
  const norm = (v) => String(v || '').replace(/\s+/g, ' ').trim();
  const visible = (el) => { const s=getComputedStyle(el), r=el.getBoundingClientRect(); return s.display!=='none' && s.visibility!=='hidden' && Number(s.opacity)!==0 && r.width>0 && r.height>0; };
  const re = /\b(PLN|EUR|USD|GBP|CAD|AUD|CHF|SEK|NOK|DKK|CZK|HUF|RON|BGN|JPY|CNY|INR|BRL|MXN|NZD|SGD|HKD|TRY|AED|ZAR|KRW|ISK|UAH|ILS|THB|PHP|MYR|IDR|VND|ARS|CLP|COP|SAR|QAR|KWD|OMR|TWD|PKR|BDT|EGP|NGN|KES|GHS|GEL|AMD|AZN|BAM|RSD|ALL|MKD|MDL|UYU|PEN)\b/i;
  const items = Array.from(document.querySelectorAll('header button, header a, nav button, nav a, button, a, select, [role="button"]')).filter(visible).map(el => {
    const text = norm(el.innerText || el.value || el.getAttribute('aria-label') || el.getAttribute('title'));
    const match = (text + ' ' + (el.getAttribute('aria-label') || '') + ' ' + (el.getAttribute('title') || '')).match(re);
    const r=el.getBoundingClientRect(); return {text, code:match ? match[1].toUpperCase() : '', top:r.top, right:r.right, tag:el.tagName.toLowerCase()};
  }).filter(x => x.code && x.top < 220).sort((a,b) => (a.text.length-b.text.length) || (b.right-a.right));
  const prices = Array.from(document.querySelectorAll('[class*="price" i], [data-price], [itemprop="price"]')).filter(visible).map(el => norm(el.innerText || el.getAttribute('content'))).filter(Boolean).slice(0,20);
  return {code: items.length ? items[0].code : '', label: items.length ? items[0].text : '', prices};
}"""


def _normal_path(path: str) -> str:
    path = urlsplit(path).path if path.startswith(("http://", "https://")) else path
    return path.rstrip("/") or "/"


def _find(links: list[dict[str, Any]], predicate) -> dict[str, Any] | None:
    return next((link for link in links if predicate(link)), None)


def _spec(case_id: str, kind: str, label: str, found: dict[str, Any] | None = None, **extra) -> dict[str, Any]:
    row = {
        "id": case_id, "kind": kind, "label": label,
        "discovered": found is not None,
        "href": found.get("href", "") if found else "",
        "hrefPath": _normal_path(found.get("path", "")) if found else "",
        "targetLabel": found.get("label", "") if found else "",
        "targetTop": found.get("top", None) if found else None,
        "targetClass": found.get("className", "") if found else "",
    }
    row.update(extra)
    if found is None:
        row["discoveryNote"] = "Expected homepage control was not found during discovery."
    return row


def build_homepage_specs(links: list[dict[str, Any]], base_url: str) -> list[dict[str, Any]]:
    """Build one test per requested homepage control, retaining missing controls as failures."""
    home_path = _normal_path(urlsplit(base_url).path)
    specs: list[dict[str, Any]] = []
    specs.append({"id": "01-homepage-load", "kind": "homepage_load", "label": "Homepage loads successfully", "discovered": True})

    home = _find(links, lambda x: x["label"].strip().lower() == "home" and _normal_path(x["path"]) == home_path)
    if not home:
        home = _find(links, lambda x: x["label"].strip().lower() == "home")
    specs.append(_spec("02-home-navigation", "home_navigation", "Home navigation", home, baseUrl=base_url))

    cart = _find(links, lambda x: bool(re.search(r"/(cart|basket)/?$", x["path"], re.I)))
    if not cart:
        cart = _find(links, lambda x: bool(re.search(r"\b(cart|shopping bag|basket)\b", x["label"] + " " + x["ariaLabel"], re.I)))
    specs.append(_spec("03-cart-round-trip", "cart_round_trip", "Cart: open and return to homepage", cart, baseUrl=base_url))

    shop = _find(links, lambda x: re.search(r"shop\s+the\s+collection", x["label"], re.I) is not None)
    if not shop:
        shop = _find(links, lambda x: re.search(r"/collections/all/?$", x["path"], re.I) is not None)
    specs.append(_spec("04-shop-the-collection", "shop_collection", "Shop the collection", shop))

    for product in EXPECTED_PRODUCTS:
        found = _find(links, lambda x, slug=product["slug"]: "/products/" in x["path"].lower() and slug.lower() in x["path"].lower())
        specs.append(_spec("product-" + product["id"], "product", product["label"] + ": open and return", found,
                           slug=product["slug"], baseUrl=base_url))

    shirts = _find(links, lambda x: "panda-shirts" in x["path"].lower())
    if not shirts:
        shirts = _find(links, lambda x: re.search(r"see\s+the\s+whole\s+collection", x["label"], re.I) and re.search(r"shirt|tee|t-shirt", x["context"], re.I))
    specs.append(_spec("collection-shirts", "shirt_collection", "T-shirts: See the whole collection", shirts))

    mugs = _find(links, lambda x: "panda-mugs" in x["path"].lower())
    if not mugs:
        mugs = _find(links, lambda x: re.search(r"see\s+the\s+whole\s+collection", x["label"], re.I) and re.search(r"mug|cup", x["context"], re.I))
    specs.append(_spec("collection-mugs", "mug_collection", "Mugs: See the whole collection", mugs))

    contacts = [x for x in links if x["label"].strip().lower() == "contact" or re.search(r"\bcontact\b", x["ariaLabel"], re.I)]
    contact_cta = _find(links, lambda x: re.search(r"/pages/contact/?$", x["path"], re.I) is not None)
    if not contact_cta:
        contact_cta = _find(contacts, lambda x: re.search(r"button|btn|cta", x["className"], re.I) or (x["top"] or 0) > 500)
    if not contact_cta and contacts:
        contact_cta = contacts[0]
    contact_footer = _find(links, lambda x: re.search(r"/contact/?$", x["path"], re.I) is not None and not re.search(r"/pages/contact/?$", x["path"], re.I))
    if not contact_footer:
        remaining = [x for x in contacts if not contact_cta or x["href"] != contact_cta["href"] or x["index"] != contact_cta["index"]]
        contact_footer = remaining[-1] if remaining else None
    specs.append(_spec("contact-cta", "contact_cta", "Contact CTA", contact_cta))
    specs.append(_spec("contact-footer-link", "contact_footer", "Footer Contact link", contact_footer))

    terms = _find(links, lambda x: re.search(r"terms-of-service|terms of service", x["path"] + " " + x["label"], re.I) is not None)
    privacy = _find(links, lambda x: re.search(r"privacy-policy|privacy policy", x["path"] + " " + x["label"], re.I) is not None)
    returns = _find(links, lambda x: re.search(r"returns-faq|returns\s*(?:&|and)\s*faq|returns\s+faq", x["path"] + " " + x["label"], re.I) is not None)
    specs.append(_spec("terms-of-service", "terms_of_service", "Terms of Service", terms))
    specs.append(_spec("privacy-policy", "privacy_policy", "Privacy Policy", privacy))
    specs.append(_spec("returns-faq", "returns_faq", "Returns & FAQ", returns))
    return specs


def discover_currency_cases(page, specs: list[dict[str, Any]]) -> dict[str, Any]:
    """Open the currency selector once and add one independent test per available currency."""
    trigger = page.evaluate(CURRENCY_TRIGGER_SCRIPT)
    if not trigger.get("found"):
        specs.append({"id": "currency-discovery", "kind": "currency_discovery", "label": "Currency selector and available currencies", "discovered": False,
                      "discoveryNote": "Could not identify a visible currency selector in the homepage header."})
        return {"found": False, "options": [], "details": "Currency selector was not found."}

    current = page.locator('[data-qa-currency-trigger="true"]')
    options: list[dict[str, Any]] = []
    if trigger.get("tag") == "select":
        for option in trigger.get("options", []):
            value = str(option.get("value", ""))
            label = str(option.get("text", "") or value)
            match = re.search(CURRENCY_PATTERN, label + " " + value, re.I)
            if match:
                options.append({"code": match.group(0).upper(), "label": label, "value": value, "mode": "select", "tag": "option", "selected": bool(option.get("selected"))})
    else:
        try:
            current.click(timeout=2500)
            page.wait_for_timeout(350)
            options = page.evaluate(CURRENCY_OPTIONS_SCRIPT)
        except Exception as exc:
            options = []
            trigger["openError"] = f"{type(exc).__name__}: {str(exc).splitlines()[0][:180]}"

    if not options:
        specs.append({"id": "currency-discovery", "kind": "currency_discovery", "label": "Currency selector and available currencies", "discovered": False,
                      "discoveryNote": "The currency selector was found, but no selectable currency options could be read.",
                      "currencyTrigger": trigger})
        return {"found": False, "trigger": trigger, "options": [], "details": "No currency options were discovered."}

    added_codes = []
    for option in options:
        code = str(option.get("code", "")).upper()
        if not code:
            continue
        label = str(option.get("label") or code)
        case_id = "currency-" + code.lower()
        if case_id in added_codes:
            continue
        added_codes.append(case_id)
        specs.append({
            "id": case_id, "kind": "currency_option", "label": f"Currency selection: {code}",
            "discovered": True, "currencyCode": code, "currencyLabel": label,
            "currencyValue": option.get("value", ""), "currencyMode": option.get("mode", "menu"),
            "currencyTrigger": {k: trigger.get(k) for k in ("tag", "text", "ariaLabel", "title", "href", "code")},
            "baseUrl": page.url,
        })
    return {"found": bool(added_codes), "trigger": trigger, "options": options, "details": f"Discovered {len(added_codes)} unique currency option(s)."}
