"""Section 03 — independent tests for each mug product and available size."""
from __future__ import annotations

from typing import Any

from tests.collection_test_helpers import run_collection_case


def test_mug_collection_case(browser_context, base_url: str, case_spec: dict[str, Any], request):
    """Open each mug from its collection and click one available size per case."""
    run_collection_case(browser_context, base_url, case_spec, request, expected_section="mugs")
