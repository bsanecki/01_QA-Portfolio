
# 03 – Playwright POM

Automated E2E tests for **SauceDemo** using **Python, Pytest and Playwright**, with a focus on the **Page Object Model (POM)**.

**SauceDemo** is a demo web application created for learning and practicing software testing and test automation.

🌐 **Website:** https://www.saucedemo.com/

## Test Coverage

- Valid and invalid login
- Locked-out user
- Product visibility
- Adding products to the cart
- Removing products from the cart
- Cart contents
- Checkout validation
- Complete checkout process

## Page Objects

The project uses separate Page Object classes for:

- Login Page
- Inventory Page
- Cart Page
- Checkout Page

This keeps page interactions and locators separated from the test scenarios.

## Technologies

- Python
- Pytest
- Playwright
- Page Object Model (POM)
