import pytest


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        driver = item.funcargs.get("driver")
        if driver:
            try:
                print(
                    f"\\n[DIAGNOSTICS] package={driver.current_package} "
                    f"activity={driver.current_activity}"
                )
                with open(f"fail_{item.name}.xml", "w", encoding="utf-8") as file:
                    file.write(driver.page_source)
            except Exception as error:
                print(f"\\n[DIAGNOSTICS] Could not save screen source: {error}")
