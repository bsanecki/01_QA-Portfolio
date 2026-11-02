from playwright.sync_api import Page


class InventoryPage:
    def __init__(self, page: Page):
        self.page = page
        self.title = page.get_by_text("Products", exact=True)
        self.products = page.locator(".inventory_item")
        self.cart_badge = page.locator(".shopping_cart_badge")
        self.cart_link = page.locator(".shopping_cart_link")
        self.sort_dropdown = page.locator(".product_sort_container")
        self.product_prices = page.locator(".inventory_item_price")

    def add_first_product_to_cart(self):
        self.page.get_by_role("button", name="Add to cart").first.click()

    def open_cart(self):
        self.cart_link.click()

    def sort_by_price_low_to_high(self):
        self.sort_dropdown.select_option("lohi")

    def displayed_prices(self) -> list[str]:
        return self.product_prices.all_text_contents()
