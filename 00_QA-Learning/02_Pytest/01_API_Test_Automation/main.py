import os
import pytest


print("========================================")
print("          API TEST AUTOMATION")
print("========================================")

url = input("Enter API URL: ")

os.environ["API_URL"] = url

print("\nRunning tests...\n")

pytest.main([
    "test_api.py",
    "-v"
])