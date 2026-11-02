from playwright.sync_api import expect

from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.inventory_page import InventoryPage


def start_checkout(inventory_page: InventoryPage) -> CheckoutPage:
    inventory_page.add_first_product_to_cart()
    inventory_page.open_cart()
    cart_page = CartPage(inventory_page.page)
    cart_page.begin_checkout()
    return CheckoutPage(inventory_page.page)


def test_checkout_requires_mandatory_information(logged_in_inventory: InventoryPage):
    checkout_page = start_checkout(logged_in_inventory)
    checkout_page.continue_checkout()

    expect(checkout_page.error_message).to_have_text("Error: First Name is required")


def test_user_can_complete_successful_checkout(logged_in_inventory: InventoryPage):
    checkout_page = start_checkout(logged_in_inventory)
    checkout_page.fill_customer_information("Test", "User", "35-001")
    checkout_page.continue_checkout()

    expect(logged_in_inventory.page.get_by_text("Checkout: Overview")).to_be_visible()
    checkout_page.finish_checkout()

    expect(checkout_page.complete_header).to_be_visible()
