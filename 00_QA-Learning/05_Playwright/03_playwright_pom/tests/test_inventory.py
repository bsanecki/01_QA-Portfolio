from playwright.sync_api import expect

from pages.inventory_page import InventoryPage


def test_products_are_displayed_after_login(logged_in_inventory: InventoryPage):
    expect(logged_in_inventory.title).to_be_visible()
    expect(logged_in_inventory.products.first).to_be_visible()
    assert logged_in_inventory.products.count() == 6


def test_product_can_be_added_to_cart(logged_in_inventory: InventoryPage):
    logged_in_inventory.add_first_product_to_cart()

    expect(logged_in_inventory.cart_badge).to_have_text("1")


def test_products_can_be_sorted_by_price_low_to_high(logged_in_inventory: InventoryPage):
    logged_in_inventory.sort_by_price_low_to_high()

    prices = [float(price.replace("$", "")) for price in logged_in_inventory.displayed_prices()]
    assert prices == sorted(prices)
