"""Create one PDF report for an entire pytest run."""

from datetime import datetime
from html import escape
from pathlib import Path
import sys
import time

import pytest


PROJECT_ROOT = Path(__file__).resolve().parent
REPORTS_DIR = PROJECT_ROOT / "reports"


def _create_run_directory(started_at):
    """Create a unique timestamped directory for this pytest run."""
    timestamp = started_at.strftime("%Y-%m-%d_%H-%M-%S")
    directory = REPORTS_DIR / timestamp
    suffix = 2

    while True:
        try:
            directory.mkdir(parents=True, exist_ok=False)
            return directory
        except FileExistsError:
            directory = REPORTS_DIR / f"{timestamp}_{suffix:02d}"
            suffix += 1


def _register_fonts():
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    font_dir = Path("/usr/share/fonts/truetype/dejavu")
    fonts = {
        "ReportDejaVu": font_dir / "DejaVuSans.ttf",
        "ReportDejaVu-Bold": font_dir / "DejaVuSans-Bold.ttf",
        "ReportDejaVu-Mono": font_dir / "DejaVuSansMono.ttf",
    }

    for name, path in fonts.items():
        if name not in pdfmetrics.getRegisteredFontNames() and path.is_file():
            pdfmetrics.registerFont(TTFont(name, str(path)))

    registered = set(pdfmetrics.getRegisteredFontNames())
    regular = "ReportDejaVu" if "ReportDejaVu" in registered else "Helvetica"
    bold = "ReportDejaVu-Bold" if "ReportDejaVu-Bold" in registered else "Helvetica-Bold"
    mono = "ReportDejaVu-Mono" if "ReportDejaVu-Mono" in registered else "Courier"
    return regular, bold, mono


def _test_status(phase_reports):
    reports = list(phase_reports.values())

    if any(report.failed for report in reports):
        return "FAILED"

    skipped = [report for report in reports if report.skipped]
    if skipped:
        return "XFAIL" if any(getattr(report, "wasxfail", None) for report in skipped) else "SKIPPED"

    if any(report.when == "call" and report.passed for report in reports):
        return "PASSED"

    return "NOT RUN"


def _paragraph(text, style, Paragraph):
    return Paragraph(escape(str(text)).replace("\n", "<br/>"), style)


def _write_run_report(session):
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        PageBreak,
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )

    config = session.config
    report_dir = getattr(config, "_pdf_report_dir", None)
    if report_dir is None:
        started_at = datetime.now().astimezone()
        report_dir = _create_run_directory(started_at)
        config._pdf_report_dir = report_dir
        config._pdf_report_started_at = started_at
        config._pdf_report_start_monotonic = time.monotonic()

    report_path = Path(report_dir) / "report.pdf"
    started_at = config._pdf_report_started_at
    finished_at = datetime.now().astimezone()
    duration = max(0.0, time.monotonic() - config._pdf_report_start_monotonic)
    regular_font, bold_font, mono_font = _register_fonts()

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="RunReportTitle", parent=styles["Title"], fontName=bold_font,
        fontSize=18, leading=22, alignment=TA_LEFT, spaceAfter=8,
    ))
    styles.add(ParagraphStyle(
        name="RunReportBody", parent=styles["BodyText"], fontName=regular_font,
        fontSize=9, leading=13, spaceAfter=5,
    ))
    styles.add(ParagraphStyle(
        name="RunReportSection", parent=styles["Heading2"], fontName=bold_font,
        fontSize=11, leading=14, spaceBefore=10, spaceAfter=5,
    ))
    styles.add(ParagraphStyle(
        name="RunReportSmall", parent=styles["BodyText"], fontName=regular_font,
        fontSize=7, leading=9, spaceAfter=1,
    ))
    styles.add(ParagraphStyle(
        name="RunReportCode", parent=styles["Code"], fontName=mono_font,
        fontSize=7, leading=9, splitLongWords=1, spaceAfter=8,
    ))

    items = list(getattr(session, "items", []))
    rows = []
    details = []
    counts = {"PASSED": 0, "FAILED": 0, "SKIPPED": 0, "XFAIL": 0, "NOT RUN": 0}
    status_colors = {
        "PASSED": colors.HexColor("#237447"),
        "FAILED": colors.HexColor("#B42318"),
        "SKIPPED": colors.HexColor("#8A6100"),
        "XFAIL": colors.HexColor("#8A6100"),
        "NOT RUN": colors.HexColor("#5B6470"),
    }

    for index, item in enumerate(items, start=1):
        phase_reports = getattr(item, "_pdf_phase_reports", {})
        status = _test_status(phase_reports)
        counts[status] = counts.get(status, 0) + 1
        test_duration = sum(getattr(rep, "duration", 0.0) for rep in phase_reports.values())
        nodeid = getattr(item, "nodeid", item.name)
        location = getattr(item, "location", (str(item.path),))[0]

        rows.append([
            Paragraph(str(index), styles["RunReportSmall"]),
            Paragraph(escape(nodeid), styles["RunReportSmall"]),
            Paragraph(
                f"<font color='{status_colors[status].hexval()}'><b>{status}</b></font>",
                styles["RunReportSmall"],
            ),
            Paragraph(f"{test_duration:.2f} s", styles["RunReportSmall"]),
        ])

        details.append((index, item, phase_reports, status, test_duration, location))

    total = len(items)
    exit_status = getattr(config, "_pdf_report_exitstatus", getattr(session, "exitstatus", None))
    if total == 0:
        summary_status = "NO TESTS" if exit_status == 5 else "FAILED"
    elif counts["FAILED"] or exit_status == 1:
        summary_status = "FAILED"
    elif exit_status not in (None, 0):
        summary_status = "INCOMPLETE"
    else:
        summary_status = "PASSED"

    story = [
        Paragraph("Pandago Appium - Full Test Run Report", styles["RunReportTitle"]),
        Paragraph(
            f"Run result: <b><font color='{status_colors.get(summary_status, colors.black).hexval()}'>{summary_status}</font></b>",
            styles["RunReportBody"],
        ),
        Paragraph(f"Started: {escape(started_at.strftime('%Y-%m-%d %H:%M:%S %Z'))}", styles["RunReportBody"]),
        Paragraph(f"Finished: {escape(finished_at.strftime('%Y-%m-%d %H:%M:%S %Z'))}", styles["RunReportBody"]),
        Paragraph(f"Total duration: {duration:.2f} seconds", styles["RunReportBody"]),
        Paragraph(f"Tests collected: {total}", styles["RunReportBody"]),
        Paragraph(
            "Results: " + " | ".join(
                f"{label}: {counts[label]}" for label in ("PASSED", "FAILED", "SKIPPED", "XFAIL", "NOT RUN")
            ),
            styles["RunReportBody"],
        ),
        Spacer(1, 4 * mm),
        Paragraph("Test summary", styles["RunReportSection"]),
    ]

    summary_rows = [[
        Paragraph("#", styles["RunReportSmall"]),
        Paragraph("Test", styles["RunReportSmall"]),
        Paragraph("Result", styles["RunReportSmall"]),
        Paragraph("Duration", styles["RunReportSmall"]),
    ]] + rows
    summary_table = Table(
        summary_rows,
        colWidths=[10 * mm, 105 * mm, 28 * mm, 25 * mm],
        repeatRows=1,
    )
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8EDF3")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#223044")),
        ("FONTNAME", (0, 0), (-1, 0), bold_font),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#CDD5DF")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.extend([summary_table, PageBreak()])

    for index, item, phase_reports, status, test_duration, location in details:
        status_color = status_colors[status].hexval()
        story.extend([
            Paragraph(f"Test {index}: {escape(item.name)}", styles["RunReportSection"]),
            Paragraph(
                f"Result: <b><font color='{status_color}'>{status}</font></b> | Duration: {test_duration:.2f} s",
                styles["RunReportBody"],
            ),
            Paragraph(f"File: {escape(str(location))}", styles["RunReportBody"]),
            Paragraph(f"Pytest ID: {escape(item.nodeid)}", styles["RunReportBody"]),
            Paragraph("Execution phases", styles["RunReportSection"]),
        ])

        phase_rows = [["Phase", "Result", "Duration"]]
        for phase in ("setup", "call", "teardown"):
            phase_report = phase_reports.get(phase)
            if phase_report is None:
                phase_rows.append([phase.title(), "Not run", "-"])
            else:
                phase_rows.append([
                    phase.title(),
                    phase_report.outcome.upper(),
                    f"{getattr(phase_report, 'duration', 0.0):.2f} s",
                ])

        phase_table = Table(phase_rows, colWidths=[35 * mm, 45 * mm, 35 * mm], repeatRows=1)
        phase_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8EDF3")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#223044")),
            ("FONTNAME", (0, 0), (-1, 0), bold_font),
            ("FONTNAME", (0, 1), (-1, -1), regular_font),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#CDD5DF")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.extend([phase_table, Spacer(1, 3 * mm)])

        for phase, phase_report in phase_reports.items():
            if (phase_report.failed or phase_report.skipped) and getattr(phase_report, "longrepr", None):
                heading = "Failure details" if phase_report.failed else "Skip details"
                story.append(Paragraph(f"{heading} - {phase.title()}", styles["RunReportSection"]))
                detail_text = str(phase_report.longrepr)
                if len(detail_text) > 18000:
                    detail_text = detail_text[:18000] + "\n... output truncated ..."
                story.append(_paragraph(detail_text, styles["RunReportCode"], Paragraph))

        seen_sections = set()
        for phase, phase_report in phase_reports.items():
            for heading, content in getattr(phase_report, "sections", []):
                content = str(content).strip()
                if not content:
                    continue
                section_key = (str(heading), content)
                if section_key in seen_sections:
                    continue
                seen_sections.add(section_key)
                story.append(Paragraph(escape(str(heading)), styles["RunReportSection"]))
                if len(content) > 12000:
                    content = content[:12000] + "\n... output truncated ..."
                story.append(_paragraph(content, styles["RunReportCode"], Paragraph))

        story.append(Spacer(1, 5 * mm))

    story.extend([
        Paragraph("Run completion", styles["RunReportSection"]),
        Paragraph(f"Pytest exit status: {escape(str(exit_status))}", styles["RunReportBody"]),
    ])

    document = SimpleDocTemplate(
        str(report_path), pagesize=A4,
        rightMargin=16 * mm, leftMargin=16 * mm,
        topMargin=15 * mm, bottomMargin=16 * mm,
        title="Pandago Appium - Full Test Run Report",
        author="Pandago Appium Tests",
    )
    document.build(story)
    print(f"\n[PDF REPORT] Full test-run report saved to: {report_path}")


@pytest.hookimpl(tryfirst=True)
def pytest_sessionstart(session):
    """Create one timestamped report directory at the start of the run."""
    started_at = datetime.now().astimezone()
    session.config._pdf_report_started_at = started_at
    session.config._pdf_report_start_monotonic = time.monotonic()
    session.config._pdf_report_dir = _create_run_directory(started_at)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    phase_reports = getattr(item, "_pdf_phase_reports", {})
    phase_reports[report.when] = report
    item._pdf_phase_reports = phase_reports


@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    """Write one PDF containing the summary and details for the complete run."""
    session.config._pdf_report_exitstatus = exitstatus
    try:
        _write_run_report(session)
    except Exception as exc:
        print(
            f"\n[PDF REPORT WARNING] Could not create the full test-run report: {exc}\n"
            "Install dependencies with: python -m pip install -r requirements.txt",
            file=sys.stderr,
        )
