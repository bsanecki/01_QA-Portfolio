import pytest
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait


# Setup
APPIUM_SERVER = "http://127.0.0.1:4723"
DEVICE_UDID = "ZY22KFW9KH"
DEVICE_NAME = "Motorola Moto G Power 5G (2024)"
SETTINGS_PACKAGE = "com.android.settings"
SETTINGS_ACTIVITY = "com.android.settings/.Settings"
WAIT_SECONDS = 10

HOMEPAGE_TITLE_ID = "com.android.settings:id/homepage_title"
SEARCH_BAR_ID = "com.android.settings:id/search_action_bar"
SEARCH_INPUT_ID = "android:id/search_src_text"
ITEM_TITLE_ID = "android:id/title"

PACKAGES_TO_RESET = [
    SETTINGS_PACKAGE,
    "com.android.settings.intelligence",
    "com.google.android.settings.intelligence",
]

MAIN_CATEGORIES = [
    "Nawigacja w systemie",
    "Sieć i internet",
    "Połączone urządzenia",
    "Personalizacja",
    "Wyświetlacz",
    "Ekran główny i ekran blokady",
    "Dźwięk i wibracje",
    "Powiadomienia",
    "Gesty",
    "Bateria",
    "Pamięć wewnętrzna",
    "Lokalizacja",
    "Ułatwienia dostępu",
    "Aplikacje",
    "Hasła, klucze dostępu i konta",
    "Bezpieczeństwo i prywatność",
    "Bezpieczeństwo i tryb alarmowy",
    "Cyfrowa równowaga i kontrola rodzicielska",
    "Google",
    "Aktualizacje systemowe",
    "System",
    "Informacje o telefonie",
]

SEARCH_TERMS = ["Bluetooth", "Wi-Fi", "Bateria", "Jasność"]


# Helpers
def reset_to_clean_state(driver):
    driver.press_keycode(3)

    for package in PACKAGES_TO_RESET:
        try:
            driver.execute_script("mobile: terminateApp", {"appId": package})
        except Exception:
            pass


@pytest.fixture
def driver():
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.automation_name = "UiAutomator2"
    options.device_name = DEVICE_NAME
    options.udid = DEVICE_UDID
    options.app_package = SETTINGS_PACKAGE
    options.app_activity = ".Settings"
    options.no_reset = True

    app_driver = webdriver.Remote(APPIUM_SERVER, options=options)
    app_driver.implicitly_wait(1)

    try:
        yield app_driver
    finally:
        try:
            reset_to_clean_state(app_driver)
        finally:
            app_driver.quit()


def normalize(text):
    return text.replace("\xa0", " ")


def open_settings_home(driver):
    reset_to_clean_state(driver)
    driver.execute_script("mobile: startActivity", {"component": SETTINGS_ACTIVITY})

    WebDriverWait(driver, WAIT_SECONDS).until(
        lambda d: any(
            element.is_displayed() and element.text == "Ustawienia"
            for element in d.find_elements(AppiumBy.ID, HOMEPAGE_TITLE_ID)
        )
    )


def scroll_down(driver):
    size = driver.get_window_size()
    result = driver.execute_script(
        "mobile: scrollGesture",
        {
            "left": int(size["width"] * 0.1),
            "top": int(size["height"] * 0.3),
            "width": int(size["width"] * 0.8),
            "height": int(size["height"] * 0.5),
            "direction": "down",
            "percent": 0.8,
        },
    )

    if isinstance(result, dict):
        result = result.get("canScrollMore", True)

    return bool(result)


def get_main_categories(driver):
    found = []

    for _ in range(15):
        for element in driver.find_elements(AppiumBy.ID, ITEM_TITLE_ID):
            title = normalize(element.text)
            if title and title not in found:
                found.append(title)

        if not scroll_down(driver):
            break

    return found


def find_category(driver, name, max_scrolls=15):
    for _ in range(max_scrolls):
        for element in driver.find_elements(AppiumBy.ID, ITEM_TITLE_ID):
            if normalize(element.text) == name:
                return element

        if not scroll_down(driver):
            break

    raise AssertionError(f'Category "{name}" was not found')


def search_for(driver, phrase):
    driver.find_element(AppiumBy.ID, SEARCH_BAR_ID).click()

    search_input = WebDriverWait(driver, WAIT_SECONDS).until(
        lambda d: d.find_element(AppiumBy.ID, SEARCH_INPUT_ID)
    )
    search_input.send_keys(phrase)


def text_views_containing(driver, phrase):
    return driver.find_elements(
        AppiumBy.XPATH,
        f'//android.widget.TextView[contains(@text, "{phrase}")]',
    )


def wait_for_homepage(driver):
    return WebDriverWait(driver, WAIT_SECONDS).until(
        lambda d: next(
            (
                element
                for element in d.find_elements(AppiumBy.ID, HOMEPAGE_TITLE_ID)
                if element.is_displayed() and element.text == "Ustawienia"
            ),
            None,
        )
    )


# Basic
def test_settings_app_is_open(driver):
    open_settings_home(driver)

    assert driver.current_package == SETTINGS_PACKAGE


def test_settings_homepage_is_visible(driver):
    open_settings_home(driver)

    title = driver.find_element(AppiumBy.ID, HOMEPAGE_TITLE_ID)

    assert title.is_displayed()
    assert title.text == "Ustawienia"



def test_settings_homepage_has_visible_categories(driver):
    open_settings_home(driver)
    visible_texts = [
        normalize(element.text)
        for element in driver.find_elements(AppiumBy.ID, ITEM_TITLE_ID)
        if element.is_displayed() and element.text.strip()
    ]

    assert "Sieć i internet" in visible_texts
    assert "Połączone urządzenia" in visible_texts


def test_settings_search_is_available(driver):
    open_settings_home(driver)

    search = driver.find_element(AppiumBy.ID, SEARCH_BAR_ID)

    assert search.is_displayed()
    assert search.is_enabled()


# Search
@pytest.mark.parametrize("phrase", SEARCH_TERMS)
def test_search_returns_results(driver, phrase):
    open_settings_home(driver)
    search_for(driver, phrase)

    WebDriverWait(driver, WAIT_SECONDS).until(
        lambda d: len(text_views_containing(d, phrase)) > 0
    )

    assert text_views_containing(driver, phrase)


def test_back_from_search_returns_home(driver):
    open_settings_home(driver)
    driver.find_element(AppiumBy.ID, SEARCH_BAR_ID).click()

    WebDriverWait(driver, WAIT_SECONDS).until(
        lambda d: d.find_element(AppiumBy.ID, SEARCH_INPUT_ID)
    )

    driver.back()
    if not any(
        element.is_displayed()
        for element in driver.find_elements(AppiumBy.ID, HOMEPAGE_TITLE_ID)
    ):
        driver.back()

    assert wait_for_homepage(driver).text == "Ustawienia"


# Categories
@pytest.mark.parametrize("category", MAIN_CATEGORIES)
def test_main_category_is_listed(driver, category):
    open_settings_home(driver)
    element = find_category(driver, category)

    assert element.is_displayed()
    assert normalize(element.text) == category


def test_network_and_internet_screen_opens(driver):
    open_settings_home(driver)
    find_category(driver, "Sieć i internet").click()

    WebDriverWait(driver, WAIT_SECONDS).until(
        lambda d: d.current_activity == ".SubSettings"
    )

    assert driver.current_package == SETTINGS_PACKAGE


@pytest.mark.parametrize(
    "category",
    ["Bateria", "Pamięć wewnętrzna", "Ułatwienia dostępu", "Informacje o telefonie", "Lokalizacja"],
)
def test_category_screen_opens(driver, category):
    open_settings_home(driver)
    find_category(driver, category).click()

    WebDriverWait(driver, WAIT_SECONDS).until(
        lambda d: not any(
            element.is_displayed()
            for element in d.find_elements(AppiumBy.ID, HOMEPAGE_TITLE_ID)
        )
    )

    assert driver.current_package == SETTINGS_PACKAGE


def test_back_navigation_returns_home(driver):
    open_settings_home(driver)
    find_category(driver, "Sieć i internet").click()

    WebDriverWait(driver, WAIT_SECONDS).until(
        lambda d: d.current_activity == ".SubSettings"
    )

    driver.back()

    assert wait_for_homepage(driver).text == "Ustawienia"


# Device
def test_android_version_is_available(driver):
    android_version = driver.capabilities.get("platformVersion")

    assert android_version is not None
    assert int(android_version.split(".")[0]) >= 14


def test_device_is_in_portrait_orientation(driver):
    open_settings_home(driver)

    assert driver.orientation == "PORTRAIT"


def test_device_is_unlocked(driver):
    open_settings_home(driver)

    assert driver.execute_script("mobile: isLocked") is False


def test_battery_level_is_valid(driver):
    info = driver.execute_script("mobile: batteryInfo")

    assert 0.0 <= info["level"] <= 1.0


def test_window_size_is_portrait(driver):
    open_settings_home(driver)
    size = driver.get_window_size()

    assert size["width"] > 0
    assert size["height"] > size["width"]


def test_device_manufacturer_is_motorola(driver):
    info = driver.execute_script("mobile: deviceInfo")

    assert info["manufacturer"].lower() == "motorola"
