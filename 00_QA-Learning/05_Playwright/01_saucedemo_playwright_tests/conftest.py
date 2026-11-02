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
def short_timeouts(page):
    page.set_default_timeout(10_000)
    page.set_default_navigation_timeout(10_000)
    expect.set_options(timeout=10_000)
