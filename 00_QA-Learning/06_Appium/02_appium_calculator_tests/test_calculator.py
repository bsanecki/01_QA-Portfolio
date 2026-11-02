import os
import pytest
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait


PACKAGE = os.getenv("CALCULATOR_PACKAGE", "com.google.android.calculator")
WAIT_SECONDS = 10

BUTTON_IDS = {
    "0": "digit_0",
    "1": "digit_1",
    "2": "digit_2",
    "3": "digit_3",
    "4": "digit_4",
    "5": "digit_5",
    "6": "digit_6",
    "7": "digit_7",
    "8": "digit_8",
    "9": "digit_9",
    "+": "op_add",
    "−": "op_sub",
    "-": "op_sub",
    "×": "op_mul",
    "*": "op_mul",
    "÷": "op_div",
    "/": "op_div",
    "=": "eq",
    ".": "dec_point",
    "%": "op_pct",
    "AC": "clr",
    "C": "clr",
}


def find_by_id(driver, resource_id):
    elements = driver.find_elements(AppiumBy.ID, f"{PACKAGE}:id/{resource_id}")
    return elements[0] if elements else None


def find_button(driver, label):
    resource_id = BUTTON_IDS.get(label)
    if resource_id:
        element = find_by_id(driver, resource_id)
        if element:
            return element

    escaped = label.replace('"', r'\"')
    selectors = [
        (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{escaped}")'),
        (AppiumBy.ACCESSIBILITY_ID, label),
        (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().description("{escaped}")'),
    ]
    for by, value in selectors:
        elements = driver.find_elements(by, value)
        if elements:
            return elements[0]
    return None


def press(driver, label):
    button = WebDriverWait(driver, WAIT_SECONDS).until(
        lambda d: find_button(d, label),
        message=f"Calculator button not found: {label!r}. "
                "Check result.txt diagnostics / UI hierarchy.",
    )
    button.click()


def press_sequence(driver, labels):
    for label in labels:
        press(driver, label)


def result_text(driver):
    for resource_id in ("result", "formula", "display"):
        element = find_by_id(driver, resource_id)
        if element:
            text = element.text.strip()
            if text:
                return text

    elements = driver.find_elements(
        AppiumBy.XPATH,
        "//*[@resource-id and (contains(@resource-id, ':id/result') "
        "or contains(@resource-id, ':id/formula') "
        "or contains(@resource-id, ':id/display'))]",
    )
    for element in reversed(elements):
        if element.text.strip():
            return element.text.strip()
    return ""


def clear_calculator(driver):
    for label in ("AC", "C"):
        button = find_button(driver, label)
        if button:
            button.click()
            return

    # Fallback: press backspace repeatedly to remove an existing expression.
    delete = driver.find_elements(AppiumBy.ACCESSIBILITY_ID, "delete")
    if delete:
        for _ in range(20):
            delete[0].click()
            delete = driver.find_elements(AppiumBy.ACCESSIBILITY_ID, "delete")
            if not delete:
                break


@pytest.fixture(autouse=True)
def calculator_ready(driver):
    driver.activate_app(PACKAGE)
    WebDriverWait(driver, WAIT_SECONDS).until(
        lambda d: d.current_package == PACKAGE
    )
    # Reset the current expression before every test.
    clear_calculator(driver)
    yield


def assert_result(driver, expected):
    text = result_text(driver)
    assert text, "Calculator result display is empty"
    normalized = (
        text.replace(",", "")
        .replace("−", "-")
        .replace(" ", "")
    )
    assert normalized.endswith(str(expected)), (
        f"Expected result ending in {expected!r}, got {text!r}"
    )


def test_calculator_opens(driver):
    assert driver.current_package == PACKAGE


def test_digit_one_can_be_pressed(driver):
    press(driver, "1")
    assert "1" in result_text(driver)


def test_digit_zero_can_be_pressed(driver):
    press(driver, "0")
    assert "0" in result_text(driver)


def test_multi_digit_number(driver):
    press_sequence(driver, ["1", "2", "3"])
    assert "123" in result_text(driver).replace(",", "")


@pytest.mark.parametrize(
    "sequence,expected",
    [
        (["2", "+", "3", "="], "5"),
        (["7", "−", "4", "="], "3"),
        (["6", "×", "3", "="], "18"),
        (["8", "÷", "2", "="], "4"),
        (["9", "+", "0", "="], "9"),
        (["5", "×", "0", "="], "0"),
        (["1", "+", "1", "="], "2"),
        (["4", "×", "4", "="], "16"),
        (["9", "−", "9", "="], "0"),
        (["1", "0", "÷", "2", "="], "5"),
    ],
)
def test_basic_calculations(driver, sequence, expected):
    press_sequence(driver, sequence)
    assert_result(driver, expected)


def test_addition_with_multi_digit_numbers(driver):
    press_sequence(driver, ["1", "2", "+", "3", "4", "="])
    assert_result(driver, "46")


def test_decimal_calculation(driver):
    press_sequence(driver, ["1", ".", "5", "+", "2", ".", "5", "="])
    assert_result(driver, "4")


def test_clear_resets_expression(driver):
    press_sequence(driver, ["8", "+", "2"])
    clear_calculator(driver)
    assert result_text(driver) in ("", "0")


def test_repeated_operation(driver):
    press_sequence(driver, ["2", "+", "3", "=", "+", "4", "="])
    assert_result(driver, "9")


@pytest.mark.parametrize("label", ["+", "−", "×", "÷", "="])
def test_operator_button_is_available(driver, label):
    assert find_button(driver, label), f"Button {label!r} was not found"


@pytest.mark.parametrize("digit", list("0123456789"))
def test_digit_button_is_available(driver, digit):
    assert find_button(driver, digit), f"Digit {digit!r} was not found"


def test_decimal_button_is_available(driver):
    assert find_button(driver, "."), "Decimal button was not found"


def test_division_by_zero_does_not_crash_app(driver):
    press_sequence(driver, ["8", "÷", "0", "="])
    assert driver.current_package == PACKAGE
    assert result_text(driver), "Calculator shows no response to division by zero"


def test_calculator_remains_foreground_after_input(driver):
    press_sequence(driver, ["4", "+", "2"])
    assert driver.current_package == PACKAGE


def test_result_display_is_present(driver):
    assert find_by_id(driver, "result") or find_by_id(driver, "formula") or result_text(driver)


def test_screen_orientation_is_supported(driver):
    assert driver.orientation in ("PORTRAIT", "LANDSCAPE")
