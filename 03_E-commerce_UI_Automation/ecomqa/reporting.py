"""English-language result storage and standalone HTML reporting."""
from __future__ import annotations

import html
import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any


def write_result(result_file: str | Path, result: dict[str, Any]) -> None:
    path = Path(result_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        existing = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
        if not isinstance(existing, list):
            existing = []
    except (OSError, json.JSONDecodeError):
        existing = []
    existing = [item for item in existing if item.get("id") != result.get("id")]
    existing.append(result)
    path.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8")


def build_html_report(
    report_dir: str | Path,
    base_url: str,
    discovery: dict[str, Any],
    results: list[dict[str, Any]],
    pytest_exit_code: int,
    section_title: str = "Section 01 — Main page",
    scope_description: str | None = None,
) -> Path:
    report_dir = Path(report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)
    status_counts = Counter(row.get("status", "UNKNOWN") for row in results)
    total = len(results)
    finished = status_counts.get("PASS", 0) + status_counts.get("FAIL", 0) + status_counts.get("SKIP", 0)
    percent = round((finished / total) * 100) if total else 0
    section_status = "FAIL" if status_counts.get("FAIL", 0) or pytest_exit_code else ("PASS" if total else "UNKNOWN")
    esc = html.escape
    rows: list[str] = []
    for index, row in enumerate(results, 1):
        status = row.get("status", "UNKNOWN")
        screenshot = row.get("screenshot")
        screenshot_link = f'<a href="{esc(screenshot)}">Open screenshot</a>' if screenshot else "—"
        rows.append(
            "<tr>"
            f"<td class='number'>{index:02}</td>"
            f"<td><span class='pill {esc(str(status).lower())}'>{esc(str(status))}</span></td>"
            f"<td><strong>{esc(row.get('label') or 'Unnamed check')}</strong><div class='muted'>{esc(row.get('id', ''))}</div></td>"
            f"<td>{esc(row.get('details', ''))}</td>"
            f"<td class='duration'>{esc(str(row.get('duration_ms', '—')))} ms</td>"
            f"<td>{screenshot_link}</td>"
            "</tr>"
        )

    screenshot_name = discovery.get("section_screenshot") or discovery.get("homepage_screenshot")
    preview_label = "Open collection screenshot" if discovery.get("section_screenshot") else "Open homepage screenshot"
    preview_link = f'<a href="{esc(screenshot_name)}">{preview_label}</a>' if screenshot_name else "Not available"
    scope_description = scope_description or (
        "Homepage navigation, cart entry and return, product cards, collection links, footer links, "
        "policies, FAQ, and currency options discovered in the currency selector."
    )
    if "Section 04" in section_title or "Cart" == section_title.split("—")[-1].strip():
        report_note = (
            "The cart section adds three fixed products only inside an isolated browser context, verifies item "
            "presence and subtotal updates, changes quantity, removes items, and opens the next checkout step "
            "without entering payment data or submitting an order. The browser context is closed after the run."
        )
    else:
        report_note = (
            "Each product workflow uses an isolated browser context. In collection sections, each unique product "
            "is opened once, then all selectable size/capacity options are clicked sequentially on that same "
            "product page. Potential repeated listing titles are reported separately; every distinct product URL "
            "is still opened and its selectable options are tested. The suite does not submit checkout forms, "
            "place orders, or perform payments."
        )
    timestamp = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    report_json = {
        "project": "E-commerce UI Automation",
        "section": section_title,
        "base_url": base_url,
        "generated_at": timestamp,
        "section_status": section_status,
        "completion_percent": percent,
        "counts": dict(status_counts),
        "total_cases": total,
        "pytest_exit_code": pytest_exit_code,
        "discovery": discovery,
        "results": results,
    }
    (report_dir / "report.json").write_text(json.dumps(report_json, ensure_ascii=False, indent=2), encoding="utf-8")

    doc = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>E-commerce QA — {esc(section_title)}</title>
<style>
:root{{--bg:#f3f5f9;--panel:#fff;--text:#182235;--muted:#637089;--line:#e0e5ee;--accent:#365b91}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:14px/1.55 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}
main{{max-width:1500px;margin:30px auto;padding:0 22px}}header{{margin:0 0 22px}}h1{{font-size:28px;line-height:1.2;margin:0 0 8px}}h2{{font-size:18px;margin:0 0 14px}}.muted{{color:var(--muted);font-size:12px;overflow-wrap:anywhere}}.panel{{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:20px;margin:16px 0;box-shadow:0 3px 14px #16254208}}
.meta{{display:flex;flex-wrap:wrap;gap:8px 20px;color:var(--muted);font-size:12px;overflow-wrap:anywhere}}.metrics{{display:grid;grid-template-columns:repeat(5,minmax(105px,1fr));gap:12px}}.metric{{background:#f8f9fc;border:1px solid var(--line);border-radius:9px;padding:14px}}.metric strong{{display:block;font-size:26px;line-height:1.2;margin-bottom:5px}}.metric span{{font-size:12px;color:var(--muted)}}
.pill{{display:inline-block;font-size:11px;font-weight:800;letter-spacing:.04em;padding:3px 9px;border-radius:5px;background:#edf0f5;color:#3d4961}}.pass{{background:#dff6e8;color:#14643b}}.fail{{background:#ffe1e1;color:#9e2222}}.skip{{background:#fff0cb;color:#805600}}.unknown{{background:#e7eaf0;color:#515d72}}.progress{{height:10px;background:#e8ebf2;border-radius:100px;overflow:hidden;margin:14px 0 6px}}.progress span{{display:block;height:100%;width:{percent}%;background:{'#c43b3b' if section_status == 'FAIL' else '#218653'};border-radius:100px}}
table{{width:100%;border-collapse:collapse;background:#fff}}th,td{{border-bottom:1px solid var(--line);padding:11px 10px;text-align:left;vertical-align:top}}th{{font-size:11px;text-transform:uppercase;letter-spacing:.05em;color:var(--muted);background:#fafbfe}}td:nth-child(4){{min-width:300px;max-width:650px;overflow-wrap:anywhere}}.table-wrap{{overflow-x:auto}}a{{color:var(--accent)}}.number,.duration{{font-variant-numeric:tabular-nums;white-space:nowrap}}.note{{color:var(--muted);font-size:13px}}code{{background:#f1f3f7;padding:2px 5px;border-radius:4px;overflow-wrap:anywhere}}
@media(max-width:900px){{.metrics{{grid-template-columns:repeat(2,minmax(100px,1fr))}}main{{padding:0 12px}}}}
</style></head><body><main>
<header><h1>E-commerce UI Automation</h1><div><strong>{esc(section_title)}</strong></div>
<div class="meta"><span>Generated: {esc(timestamp)}</span><span>Store: <code>{esc(base_url)}</code></span><span>{preview_link}</span></div></header>
<section class="panel"><h2>Section result <span class="pill {section_status.lower()}">{section_status}</span></h2>
<div class="metrics"><div class="metric"><strong>{total}</strong><span>Individual result rows</span></div>
<div class="metric"><strong>{status_counts.get('PASS', 0)}</strong><span>PASS — expected behavior observed</span></div>
<div class="metric"><strong>{status_counts.get('FAIL', 0)}</strong><span>FAIL — defect or unexpected behavior</span></div>
<div class="metric"><strong>{status_counts.get('SKIP', 0)}</strong><span>SKIP — safely not executed</span></div>
<div class="metric"><strong>{percent}%</strong><span>Results reported</span></div></div>
<div class="progress" aria-label="Checks completed"><span></span></div><div class="muted">{finished} of {total} result rows reported · pytest exit code {pytest_exit_code}</div>
<p class="note">A FAIL is not automatically a problem with the automation. It can be a real store defect, for example a link returning HTTP 404. Test-engine or browser errors are recorded with their own details so they can be separated from storefront defects.</p></section>
<section class="panel"><h2>Individual check results</h2><div class="table-wrap"><table><thead><tr><th>#</th><th>Status</th><th>Check</th><th>Result details</th><th>Duration</th><th>Evidence</th></tr></thead><tbody>{''.join(rows) if rows else '<tr><td colspan="6">No test results were recorded.</td></tr>'}</tbody></table></div></section>
<section class="panel"><h2>Scope</h2><p>{esc(scope_description)}</p>
<p>{esc(report_note)}</p></section>
</main></body></html>"""
    path = report_dir / "report.html"
    path.write_text(doc, encoding="utf-8")
    return path
