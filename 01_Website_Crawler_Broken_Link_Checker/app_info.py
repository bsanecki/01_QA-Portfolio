"""Static texts and constants of the More screens (How to Use, HTTP Status
Codes, About). No Tkinter in here.

Author name and PayPal support link are set below.
"""

from dataclasses import dataclass

from models import (
    CAT_BROKEN,
    CAT_OK,
    CAT_REDIRECT,
    CAT_UNVERIFIED,
    LinkResult,
)

APP_NAME = "Website Crawler & Broken Link Checker"

# ---------------------------------------------------------------------------
# Author / PayPal
# ---------------------------------------------------------------------------

AUTHOR_NAME = "Bartosz Sanecki"

PAYPAL_URL = "https://paypal.me/bsanecki"

# ---------------------------------------------------------------------------
# About
# ---------------------------------------------------------------------------

ABOUT_DESCRIPTION = (
    "A Python-based QA tool for website crawling,\n"
    "link checking and JavaScript-enabled web testing."
)

TECHNOLOGIES = (
    "Python", "Playwright", "Requests", "BeautifulSoup", "Tkinter", "pytest",
)

SUPPORT_TEXT = (
    "If this tool is useful to you, you can voluntarily support the "
    "project via PayPal. Thank you!"
)

# ---------------------------------------------------------------------------
# Result categories (same names as the scan / report)
# ---------------------------------------------------------------------------

CATEGORY_LABELS = {
    CAT_OK: "OK",
    CAT_REDIRECT: "Redirect",
    CAT_BROKEN: "Broken",
    CAT_UNVERIFIED: "Unverified",
}

# ---------------------------------------------------------------------------
# How to Use
# ---------------------------------------------------------------------------

HOW_TO_USE = (
    ("Full Website Scan",
     "Enter the start URL (http:// or https://), choose Crawl depth and "
     "Crawl mode, then press START SCAN. The site is crawled and every link "
     "found (pages, images, scripts, styles, external links) is checked. "
     "When the scan completes, a report opens."),

    ("Single Link Check",
     "Enter one URL and press CHECK. You get the HTTP status, category, "
     "response time, final URL, redirects and error details, classified "
     "exactly like in a full scan."),

    ("Crawl Depth",
     "0 = only the start page. N = pages up to N link-hops from the start "
     "page are downloaded and searched for links. Links found on them are "
     "always checked; pages beyond the depth are checked but not crawled. "
     "Unlimited crawls the whole site."),

    ("HTTP mode",
     "Default. Fast, needs no browser. Reads the HTML as the server sends "
     "it, so links created by JavaScript are not seen."),

    ("Auto",
     "Starts like HTTP. Pages whose HTML contains no links are rendered "
     "with the first browser found (Chromium, Chrome, Edge, Brave, Firefox, "
     "Opera). Without any browser it stays in HTTP mode."),

    ("Chromium / Firefox",
     "Render every page with JavaScript using Playwright's own browser. "
     "Install once with:  python -m pip install playwright  and  "
     "python -m playwright install chromium  (or firefox)."),

    ("Chrome / Edge / Brave / Opera",
     "Render every page with JavaScript using the copy of that browser "
     "installed on your computer (Playwright package still required). "
     "If the browser is missing you can continue in HTTP mode."),

    ("OK / Redirect / Broken / Unverified",
     "OK: the link works (2xx).\n"
     "Redirect: the link was redirected (3xx); the chain is shown.\n"
     "Broken: the target is gone (404, 410) or redirects in a loop.\n"
     "Unverified: no reliable answer - 401, 403, 429, other 4xx, 5xx, "
     "timeouts, DNS, SSL or connection errors. Not necessarily broken: "
     "open the link in a browser to confirm."),

    ("STOP",
     "Ends a running scan within moments. A stopped scan does not open a "
     "report. Start a new scan when you are ready."),

    ("Reports / Excel",
     "A finished scan opens a report with Summary, Problems, Redirects and "
     "All Links tabs. DOWNLOAD REPORT saves it as an Excel (.xlsx) file "
     "that also lists every page a link was found on."),
)

# ---------------------------------------------------------------------------
# HTTP status codes
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class StatusInfo:
    code: str
    name: str
    category: str
    text: str

    @property
    def category_label(self):
        return CATEGORY_LABELS[self.category]


# (status, explanation)
_STATUS_TEXTS = (
    (200, "The link works."),
    (301, "The page moved permanently. The checker follows the redirect and "
          "shows the chain and the final status."),
    (302, "Temporary redirect. Followed and reported like 301."),
    (400, "The server rejected the request. Open the link in a browser to "
          "confirm."),
    (401, "Login required. The link may be fine for signed-in users."),
    (403, "Access refused - often bot protection. The link may work in a "
          "browser."),
    (404, "The page does not exist."),
    (408, "The server gave up waiting for the request. Retried once."),
    (410, "The page was removed for good."),
    (429, "Too many requests (rate limiting). Retried once after a short "
          "wait."),
    (500, "Server error, often temporary. Retried once."),
    (502, "A gateway received an invalid answer from another server. "
          "Retried once."),
    (503, "Server overloaded or in maintenance. Retried once."),
)

_NO_RESPONSE_TEXTS = (
    ("No response", "Timeout / DNS / SSL / connection error",
     LinkResult("", None, "", 0.0, error_type="TIMEOUT"),
     "No HTTP answer was received (retried once). Check the URL and your "
     "connection."),
    ("Redirect loop", "Too many redirects",
     LinkResult("", None, "", 0.0, error_type="TOO MANY REDIRECTS"),
     "The link redirects in a circle or more than 10 times."),
)

STATUS_NOTE = (
    "A redirect that ends in 404 or 410 is reported as Broken. "
    "Unverified is never counted as Broken."
)


def status_code_reference():
    """Rows of the HTTP Status Codes screen. The category of every row comes
    from LinkResult.category, the classifier the scan itself uses, so this
    reference cannot drift away from the real behaviour."""
    from http import HTTPStatus

    rows = []

    for status, text in _STATUS_TEXTS:
        result = LinkResult("", status, "", 0.0)

        rows.append(
            StatusInfo(
                str(status),
                HTTPStatus(status).phrase,
                result.category,
                text,
            )
        )

    for code, name, result, text in _NO_RESPONSE_TEXTS:
        rows.append(
            StatusInfo(
                code,
                name,
                result.category,
                text,
            )
        )

    return rows
