import pytest
from playwright.sync_api import expect


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    return {
        **browser_type_launch_args,
        "args": [
            *browser_type_launch_args.get("args", []),
            "--lang=en-US",
            "--accept-lang=en-US",
            "--disable-translate",
            "--disable-features=Translate,TranslateUI,TranslateSubFrames",
        ],
    }


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "locale": "en-US",
        "viewport": {"width": 1280, "height": 720},
    }


@pytest.fixture(autouse=True)
def configure_timeouts(page):
    page.set_default_timeout(10_000)
    page.set_default_navigation_timeout(15_000)
    expect.set_options(timeout=10_000)
    for ad_domain in (
        "**/*googlesyndication.com/**",
        "**/*doubleclick.net/**",
        "**/*googleadservices.com/**",
    ):
        page.route(ad_domain, lambda route: route.abort())
    page.add_locator_handler(
        page.locator(".fc-dialog-overlay"),
        lambda: page.locator(".fc-consent-root").evaluate(
            "element => element.remove()"
        ),
    )
