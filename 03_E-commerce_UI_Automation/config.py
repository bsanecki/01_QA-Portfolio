"""Runtime configuration for the E-commerce QA portfolio project."""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE_URL = os.getenv(
    "BASE_URL", "https://pandapocket-shop.fourthwall.com/en-pln/"
).strip()
if not BASE_URL:
    BASE_URL = "https://pandapocket-shop.fourthwall.com/en-pln/"
if not BASE_URL.endswith("/"):
    BASE_URL += "/"

REPORTS_DIR = Path(os.getenv("REPORTS_DIR", ROOT / "reports"))
VIEWPORT = {"width": 1440, "height": 1000}
NAVIGATION_TIMEOUT_MS = 15_000
ACTION_TIMEOUT_MS = 4_000
DISCOVERY_WAIT_MS = 1_000
POST_CLICK_WAIT_MS = 900

EXPECTED_PRODUCTS = [
    {
        "id": "tshirt-boyfriend", "slug": "this-is-my-boyfriend-cute-bubu-dudu-unisex-t-shirt-2",
        "label": "T-shirt: This Is My Boyfriend",
    },
    {
        "id": "tshirt-back-off", "slug": "back-off-i-have-bubu-funny-bubu-dudu-unisex-t-shirt",
        "label": "T-shirt: Back Off, I Have Bubu",
    },
    {
        "id": "tshirt-punching-bag", "slug": "my-boyfriend-is-my-punching-bag-funny-bubu-dudu-unisex-t-shirt",
        "label": "T-shirt: My Boyfriend Is My Punching Bag",
    },
    {
        "id": "tshirt-trouble-maker", "slug": "dudu-certified-trouble-maker-funny-bubu-dudu-unisex-t-shirt",
        "label": "T-shirt: Dudu Certified Trouble Maker",
    },
    {
        "id": "mug-patience", "slug": "bubus-patience-1-funny-bubu-dudu-couple-mug",
        "label": "Mug: Bubu's Patience: 1%",
    },
    {
        "id": "mug-always-mine", "slug": "you-will-always-be-mine-cute-bubu-dudu-couple-mug",
        "label": "Mug: You Will Always Be Mine",
    },
    {
        "id": "mug-washing-dudu", "slug": "dudu-washing-bubu-for-the-first-time-in-a-year-funny-bubu-dudu-mug",
        "label": "Mug: Dudu Washing Bubu",
    },
    {
        "id": "mug-flower", "slug": "flower-for-my-dudu-cute-bubu-dudu-couple-mug",
        "label": "Mug: Flower for My Dudu",
    },
]
