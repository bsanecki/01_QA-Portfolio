import os

BASE_URL = os.getenv("API_BASE_URL", "https://jsonplaceholder.typicode.com").rstrip("/")
REQUEST_TIMEOUT = float(os.getenv("API_TIMEOUT", "10"))
MAX_RESPONSE_TIME_SECONDS = float(os.getenv("API_MAX_RESPONSE_TIME", "3"))
