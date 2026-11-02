from playwright.sync_api import Page


class CheckoutPage:
    def __init__(self, page: Page):
        self.page = page
        self.first_name_input = page.get_by_role("textbox", name="First Name")
        self.last_name_input = page.get_by_role("textbox", name="Last Name")
        self.postal_code_input = page.get_by_role("textbox", name="Zip/Postal Code")
        self.continue_button = page.get_by_role("button", name="Continue")
        self.finish_button = page.get_by_role("button", name="Finish")
        self.error_message = page.locator('[data-test="error"]')
        self.complete_header = page.get_by_text("Thank you for your order!")

    def continue_checkout(self):
        self.continue_button.click()

    def fill_customer_information(
        self, first_name: str, last_name: str, postal_code: str
    ):
        self.first_name_input.fill(first_name)
        self.last_name_input.fill(last_name)
        self.postal_code_input.fill(postal_code)

    def finish_checkout(self):
        self.finish_button.click()
