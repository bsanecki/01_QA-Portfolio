from uuid import uuid4

from playwright.sync_api import Page, expect


BASE_URL = "https://automationexercise.com/"


def new_user() -> dict[str, str]:
    token = uuid4().hex[:8]
    return {
        "name": f"Test User {token}",
        "email": f"test_{token}@example.com",
        "password": "TestPassword123!",
    }


def open_login_page(page: Page):
    page.goto(BASE_URL)
    page.get_by_role("link", name="Signup / Login").click()
    expect(page.get_by_text("New User Signup!")).to_be_visible()


def register_user(page: Page, user: dict[str, str]):
    open_login_page(page)
    page.locator('[data-qa="signup-name"]').fill(user["name"])
    page.locator('[data-qa="signup-email"]').fill(user["email"])
    page.get_by_role("button", name="Signup").click()

    page.locator("#id_gender1").check()
    page.locator('[data-qa="password"]').fill(user["password"])
    page.locator('[data-qa="days"]').select_option("10")
    page.locator('[data-qa="months"]').select_option("5")
    page.locator('[data-qa="years"]').select_option("1995")
    page.locator('[data-qa="first_name"]').fill("Test")
    page.locator('[data-qa="last_name"]').fill("User")
    page.locator('[data-qa="address"]').fill("123 Test Street")
    page.locator('[data-qa="country"]').select_option("United States")
    page.locator('[data-qa="state"]').fill("Test State")
    page.locator('[data-qa="city"]').fill("Test City")
    page.locator('[data-qa="zipcode"]').fill("12345")
    page.locator('[data-qa="mobile_number"]').fill("5551234567")
    page.get_by_role("button", name="Create Account").click()

    expect(page.get_by_text("Account Created!")).to_be_visible()
    page.get_by_role("link", name="Continue").click()
    expect(page.get_by_text(f"Logged in as {user['name']}")).to_be_visible()


def login(page: Page, user: dict[str, str]):
    open_login_page(page)
    page.locator('[data-qa="login-email"]').fill(user["email"])
    page.locator('[data-qa="login-password"]').fill(user["password"])
    page.get_by_role("button", name="Login").click()
    expect(page.get_by_text(f"Logged in as {user['name']}")).to_be_visible()


def add_product_to_cart(page: Page, product_index: int):
    product_id = product_index + 1
    page.locator(f'.add-to-cart[data-product-id="{product_id}"]').first.click()
    expect(page.get_by_text("Added!")).to_be_visible()


def test_homepage_loads_correctly(page: Page):
    page.goto(BASE_URL)

    expect(page.get_by_role("link", name="Home")).to_be_visible()
    expect(page.get_by_role("link", name="Products")).to_be_visible()
    expect(page.locator("#slider")).to_be_visible()


def test_user_can_register_a_new_account(page: Page):
    register_user(page, new_user())


def test_user_can_log_in_with_valid_credentials(page: Page):
    user = new_user()
    register_user(page, user)
    page.get_by_role("link", name="Logout").click()

    login(page, user)


def test_login_fails_with_invalid_credentials(page: Page):
    open_login_page(page)
    page.locator('[data-qa="login-email"]').fill("invalid@example.com")
    page.locator('[data-qa="login-password"]').fill("wrong-password")
    page.get_by_role("button", name="Login").click()

    expect(page.get_by_text("Your email or password is incorrect!")).to_be_visible()


def test_user_can_log_out(page: Page):
    user = new_user()
    register_user(page, user)

    page.get_by_role("link", name="Logout").click()

    expect(page.get_by_text("Login to your account")).to_be_visible()
    expect(page.get_by_text("New User Signup!")).to_be_visible()


def test_products_can_be_searched(page: Page):
    page.goto(BASE_URL)
    page.get_by_role("link", name="Products").click()
    page.get_by_placeholder("Search Product").fill("Blue Top")
    page.locator("#submit_search").click()

    expect(page.get_by_text("Searched Products")).to_be_visible()
    expect(page.get_by_text("Blue Top", exact=True).first).to_be_visible()


def test_product_details_are_displayed(page: Page):
    page.goto(BASE_URL)
    page.get_by_role("link", name="Products").click()
    page.get_by_role("link", name="View Product").first.click()

    expect(page.get_by_role("heading", name="Blue Top")).to_be_visible()
    expect(page.get_by_text("Category:")).to_be_visible()
    expect(page.get_by_text("Availability:")).to_be_visible()


def test_product_can_be_added_to_cart(page: Page):
    page.goto(BASE_URL)
    add_product_to_cart(page, 0)
    page.get_by_role("link", name="View Cart").click()

    expect(page.locator("#product-1")).to_contain_text("Blue Top")


def test_multiple_products_are_added_to_cart(page: Page):
    page.goto(BASE_URL)
    add_product_to_cart(page, 0)
    page.get_by_role("button", name="Continue Shopping").click()
    add_product_to_cart(page, 1)
    page.get_by_role("link", name="View Cart").click()

    expect(page.locator("#product-1")).to_contain_text("Blue Top")
    expect(page.locator("#product-2")).to_contain_text("Men Tshirt")


def test_complete_checkout_order_flow(page: Page):
    user = new_user()
    register_user(page, user)
    add_product_to_cart(page, 0)
    page.get_by_role("link", name="View Cart").click()
    page.get_by_text("Proceed To Checkout", exact=True).click()

    expect(page.get_by_text("Address Details")).to_be_visible()
    expect(page.get_by_text("Review Your Order")).to_be_visible()
    page.locator('textarea[name="message"]').fill("Test order")
    page.get_by_role("link", name="Place Order").click()

    page.locator('[data-qa="name-on-card"]').fill("Test User")
    page.locator('[data-qa="card-number"]').fill("4111111111111111")
    page.locator('[data-qa="cvc"]').fill("123")
    page.locator('[data-qa="expiry-month"]').fill("12")
    page.locator('[data-qa="expiry-year"]').fill("2030")
    page.get_by_role("button", name="Pay and Confirm Order").click()

    expect(page.get_by_text("Order Placed!")).to_be_visible()
