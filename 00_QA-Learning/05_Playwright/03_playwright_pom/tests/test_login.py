from playwright.sync_api import Page, expect

from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage


def test_successful_login(page: Page):
    login_page = LoginPage(page)
    login_page.open()
    login_page.login("standard_user", "secret_sauce")

    expect(page).to_have_url("https://www.saucedemo.com/inventory.html")
    expect(InventoryPage(page).title).to_be_visible()


def test_login_with_invalid_password(page: Page):
    login_page = LoginPage(page)
    login_page.open()
    login_page.login("standard_user", "wrong_password")

    expect(login_page.error_message).to_contain_text(
        "Username and password do not match"
    )


def test_locked_out_user_cannot_log_in(page: Page):
    login_page = LoginPage(page)
    login_page.open()
    login_page.login("locked_out_user", "secret_sauce")

    expect(login_page.error_message).to_contain_text("Sorry, this user has been locked out")
