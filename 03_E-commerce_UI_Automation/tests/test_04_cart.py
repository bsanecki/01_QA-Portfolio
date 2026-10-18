"""Section 04 — cart lifecycle: add, quantity, subtotal, remove, checkout step."""
from __future__ import annotations

from ecomqa.cart_testing import run_cart_workflow


def test_cart_workflow(browser_context, base_url: str, request):
    """Exercise a full cart workflow in one isolated browser context and report each action."""
    run_cart_workflow(browser_context, base_url, request)
