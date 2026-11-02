import pytest
from playwright.sync_api import Page, expect


BASE_URL = "https://www.saucedemo.com/"


def login(page: Page, username: str = "standard_user", password: str = "secret_sauce"):
    page.goto(BASE_URL)
    page.get_by_role("textbox", name="Username").fill(username)
    page.get_by_role("textbox", name="Password").fill(password)
    page.get_by_role("button", name="Login").click()


def test_login_with_valid_credentials(page: Page):
    login(page)

    expect(page).to_have_url("https://www.saucedemo.com/inventory.html")
    expect(page.get_by_text("Products")).to_be_visible()


def test_login_with_invalid_password(page: Page):
    page.goto(BASE_URL)
    page.get_by_role("textbox", name="Username").fill("standard_user")
    page.get_by_role("textbox", name="Password").fill("wrong_password")
    page.get_by_role("button", name="Login").click()

    expect(page.get_by_text("Epic sadface: Username and password do not match any user in this service")).to_be_visible()


def test_locked_out_user_cannot_login(page: Page):
    page.goto(BASE_URL)
    page.get_by_role("textbox", name="Username").fill("locked_out_user")
    page.get_by_role("textbox", name="Password").fill("secret_sauce")
    page.get_by_role("button", name="Login").click()

    expect(page.get_by_text("Epic sadface: Sorry, this user has been locked out.")).to_be_visible()


def test_inventory_contains_products(page: Page):
    login(page)

    expect(page.get_by_text("Products")).to_be_visible()
    expect(page.get_by_text("Sauce Labs Backpack")).to_be_visible()
    expect(page.get_by_text("Sauce Labs Bike Light")).to_be_visible()
    expect(page.get_by_text("Sauce Labs Bolt T-Shirt", exact=True)).to_be_visible()


def test_add_product_to_cart(page: Page):
    login(page)

    page.get_by_role("button", name="Add to cart").first.click()

    cart_badge = page.locator(".shopping_cart_badge")
    expect(cart_badge).to_have_text("1")


def test_remove_product_from_cart(page: Page):
    login(page)

    page.get_by_role("button", name="Add to cart").first.click()
    page.get_by_role("button", name="Remove").first.click()

    expect(page.locator(".shopping_cart_badge")).not_to_be_visible()


def test_cart_contains_selected_product(page: Page):
    login(page)

    page.get_by_role("button", name="Add to cart").first.click()
    page.locator(".shopping_cart_link").click()

    expect(page).to_have_url("https://www.saucedemo.com/cart.html")
    expect(page.get_by_text("Sauce Labs Backpack")).to_be_visible()


def test_product_sorting_low_to_high(page: Page):
    login(page)

    page.locator(".product_sort_container").select_option("lohi")

    prices = page.locator(".inventory_item_price").all_text_contents()
    numeric_prices = [float(price.replace("$", "")) for price in prices]

    assert numeric_prices == sorted(numeric_prices)


def test_checkout_required_fields(page: Page):
    login(page)

    page.get_by_role("button", name="Add to cart").first.click()
    page.locator(".shopping_cart_link").click()
    page.get_by_role("button", name="Checkout").click()

    expect(page).to_have_url("https://www.saucedemo.com/checkout-step-one.html")

    page.get_by_role("button", name="Continue").click()

    expect(page.get_by_text("Error: First Name is required")).to_be_visible()


def test_complete_checkout(page: Page):
    login(page)

    page.get_by_role("button", name="Add to cart").first.click()
    page.locator(".shopping_cart_link").click()
    page.get_by_role("button", name="Checkout").click()

    page.get_by_role("textbox", name="First Name").fill("Test")
    page.get_by_role("textbox", name="Last Name").fill("User")
    page.get_by_role("textbox", name="Zip/Postal Code").fill("35-001")
    page.get_by_role("button", name="Continue").click()

    expect(page.get_by_text("Checkout: Overview")).to_be_visible()
    expect(page.get_by_text("Sauce Labs Backpack")).to_be_visible()

    page.get_by_role("button", name="Finish").click()

    expect(page.get_by_text("Thank you for your order!")).to_be_visible()
    expect(page.get_by_text("Your order has been dispatched, and will arrive just as fast as the pony can get there!")).to_be_visible()
