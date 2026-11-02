from playwright.sync_api import Page


class CartPage:
    def __init__(self, page: Page):
        self.page = page
        self.cart_items = page.locator(".cart_item")
        self.first_item_name = page.locator(".inventory_item_name").first
        self.remove_button = page.get_by_role("button", name="Remove").first
        self.checkout_button = page.get_by_role("button", name="Checkout")

    def remove_first_product(self):
        self.remove_button.click()

    def begin_checkout(self):
        self.checkout_button.click()
