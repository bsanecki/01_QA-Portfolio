import re
from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://pandapocket-shop.fourthwall.com/en-pln")
    page.get_by_role("link", name="Back Off, I Have Bubu – Funny").click()
    page.locator("label").filter(has_text="M").click()
    page.get_by_role("radio", name="M").check()
    page.get_by_test_id("product.add.to.cart").click()
    page.get_by_role("link", name="View Cart").click()
    page.close()

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
