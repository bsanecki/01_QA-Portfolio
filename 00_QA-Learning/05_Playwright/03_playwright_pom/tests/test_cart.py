from playwright.sync_api import expect

from pages.cart_page import CartPage
from pages.inventory_page import InventoryPage


def test_added_product_appears_in_cart(logged_in_inventory: InventoryPage):
    logged_in_inventory.add_first_product_to_cart()
    logged_in_inventory.open_cart()
    cart_page = CartPage(logged_in_inventory.page)

    expect(cart_page.first_item_name).to_have_text("Sauce Labs Backpack")


def test_product_can_be_removed_from_cart(logged_in_inventory: InventoryPage):
    logged_in_inventory.add_first_product_to_cart()
    logged_in_inventory.open_cart()
    cart_page = CartPage(logged_in_inventory.page)
    cart_page.remove_first_product()

    expect(cart_page.cart_items).to_have_count(0)
