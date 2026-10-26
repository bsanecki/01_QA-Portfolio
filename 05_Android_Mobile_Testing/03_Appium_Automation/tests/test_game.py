
import random
import re
import time

import pytest
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait

from config.settings import (
    ANDROID_DEVICE_NAME, ANDROID_UDID, APPIUM_SERVER_URL,
    PANDAGO_APP_PACKAGE,
)
from test_navigation import (
    DUEL_TEXT, HOME_TEXT, CATEGORY_ID,
    _find_text, _id_elements, _open_mode, _scroll_to_text,
    _text, _text_elements, _visible, _wait_id, _wait_text,
)

SEARCH_TITLE = ("Quiz Battle",)
SEARCHING = (
    "Wyszukiwanie przeciwnika...", "Searching for opponent...",
    "Szukamy rywala...", "Searching for rival...",
)
BATTLE_STARTED = ("Bitwa rozpoczęta!", "Battle started!")
RESULT_HEADINGS = (
    "Zwycięstwo!", "Victory!", "Przegrana", "Defeat", "Remis!", "Draw!",
)
RESULT_CORRECT_LABELS = ("Poprawne odpowiedzi:", "Correct answers:")
RESULT_MENU = ("MENU", "Menu")


@pytest.fixture(scope="module")
def driver():
    """Keep the same app/session between stage tests."""
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.automation_name = "UiAutomator2"
    options.device_name = ANDROID_DEVICE_NAME
    options.no_reset = True
    options.new_command_timeout = 300
    if ANDROID_UDID:
        options.udid = ANDROID_UDID

    session = webdriver.Remote(
        command_executor=APPIUM_SERVER_URL,
        options=options,
    )
    try:
        yield session
    finally:
        session.quit()


def _categories(driver):
    elements = [
        element for element in driver.find_elements(AppiumBy.ID, CATEGORY_ID)
        if _visible(element) and _text(element)
    ]
    return sorted(
        elements,
        key=lambda element: (
            element.rect.get("y", 0),
            element.rect.get("x", 0),
        ),
    )


def _select_random_category(driver):
    categories = WebDriverWait(
        driver, 15, poll_frequency=0.3
    ).until(lambda current: _categories(current) or False)

    selected = random.choice(categories)
    label = _text(selected)
    rect = selected.rect
    cx = rect["x"] + rect["width"] / 2
    cy = rect["y"] + rect["height"] / 2

    cards = [
        card for card in _id_elements(driver, "category_card")
        if _visible(card)
    ]
    if cards:
        card = min(
            cards,
            key=lambda item: (
                abs(item.rect["x"] + item.rect["width"] / 2 - cx)
                + abs(item.rect["y"] + item.rect["height"] / 2 - cy)
            ),
        )
        rect = card.rect
        cx = rect["x"] + rect["width"] / 2
        cy = rect["y"] + rect["height"] / 2

    driver.execute_script(
        "mobile: clickGesture", {"x": round(cx), "y": round(cy)}
    )
    print(f"[GAME] Selected category: {label}")
    return label


def _question_number(driver):
    pattern = re.compile(
        r"\b(?:PYTANIE|QUESTION)\s+(\d+)\s*/\s*8\b",
        re.IGNORECASE,
    )
    for element in driver.find_elements(AppiumBy.XPATH, "//*[@text]"):
        if _visible(element):
            match = pattern.search(_text(element))
            if match:
                return int(match.group(1))
    return None


def _result_visible(driver):
    return bool(_find_text(driver, RESULT_HEADINGS, exact=True))


def _matchmaking_state(driver):
    if (
        _find_text(driver, SEARCH_TITLE, exact=True)
        and _find_text(driver, SEARCHING)
    ):
        return "searching"
    if _find_text(driver, BATTLE_STARTED, exact=True):
        return "battle intro"
    if _question_number(driver) is not None:
        return "question"
    return False


def _answer_options(driver):
    height = driver.get_window_size()["height"]
    choices = {}

    for letter in ("A", "B", "C", "D"):
        for element in _text_elements(driver, (letter,), exact=True):
            if not _visible(element):
                continue
            rect = element.rect
            y = round(rect["y"] + rect["height"] / 2)
            if height * 0.30 <= y <= height * 0.97:
                choices.setdefault(letter, y)

    return list(choices.items())


def _tap_random_answer(driver, number):
    choices = WebDriverWait(
        driver, 10, poll_frequency=0.3
    ).until(lambda current: _answer_options(current) or False)

    letter, y = random.choice(choices)
    width = driver.get_window_size()["width"]

    driver.execute_script(
        "mobile: clickGesture", {"x": round(width * 0.52), "y": y}
    )
    print(f"[GAME] Question {number}/8: chose {letter}.")


def _wait_next_question_or_result(driver, previous, timeout=40):
    deadline = time.monotonic() + timeout
    blank_since = None
    pressed_back = False

    while time.monotonic() < deadline:
        if _result_visible(driver):
            return "result"

        number = _question_number(driver)
        if number is not None:
            blank_since = None
            if number > previous:
                return number
        else:
            blank_since = blank_since or time.monotonic()
            if not pressed_back and time.monotonic() - blank_since > 8:
                # The result page can launch an interstitial that hides its UI.
                driver.back()
                pressed_back = True
                blank_since = time.monotonic()

        time.sleep(0.3)

    raise TimeoutException(
        f"After question {previous}, no next question or result appeared."
    )


def _wait_result_screen(driver, timeout=55):
    deadline = time.monotonic() + timeout
    blank_since = None
    pressed_back = False

    while time.monotonic() < deadline:
        if _result_visible(driver):
            return True

        if _question_number(driver) is None:
            blank_since = blank_since or time.monotonic()
            if not pressed_back and time.monotonic() - blank_since > 8:
                driver.back()
                pressed_back = True
                blank_since = time.monotonic()
        else:
            blank_since = None

        time.sleep(0.3)

    raise TimeoutException("The win/loss/draw result screen did not appear.")


# Tests below are sequential. Run: pytest -v tests/test_game.py


def test_game_01_duel_1v1_opens_category_picker(driver):
    """Stage 1: enter 1v1 and verify that categories are displayed."""
    _open_mode(driver, DUEL_TEXT)
    _wait_id(driver, "categories_recycler_view", timeout=12)

    categories = _categories(driver)
    assert len(categories) >= 2, "The category picker did not load categories."

    print(
        f"[GAME] PASS: 1v1 category picker opened "
        f"({len(categories)} visible)."
    )


def test_game_02_category_selection_starts_matchmaking(driver):
    """Stage 2: select a random category and check that search starts."""
    category = _select_random_category(driver)

    state = WebDriverWait(
        driver, 25, poll_frequency=0.3
    ).until(_matchmaking_state)

    assert state in {"searching", "battle intro", "question"}, (
        f"No matchmaking/game screen appeared for category {category!r}."
    )
    print(f"[GAME] PASS: selected {category!r}; state={state}.")


def test_game_03_matchmaking_starts_duel(driver):
    """Stage 3: wait until gameplay displays a question."""
    number = WebDriverWait(
        driver, 75, poll_frequency=0.3
    ).until(lambda current: _question_number(current) or False)

    assert 1 <= number <= 8, f"Unexpected question number: {number}."
    print(f"[GAME] PASS: duel started; question {number}/8 is visible.")


def test_game_04_random_answers_complete_match_and_show_result(driver):
    """Stage 4: randomly answer all questions and verify the result screen."""
    answered = []
    deadline = time.monotonic() + 260

    while len(set(answered)) < 8 and time.monotonic() < deadline:
        if _result_visible(driver):
            break

        number = _question_number(driver)
        if number is None:
            time.sleep(0.3)
            continue

        if number in answered:
            _wait_next_question_or_result(driver, number, timeout=35)
            continue

        assert 1 <= number <= 8, f"Unexpected question index: {number}."
        _tap_random_answer(driver, number)
        answered.append(number)

        if (
            _wait_next_question_or_result(driver, number, timeout=40)
            == "result"
        ):
            break

    assert len(set(answered)) == 8, (
        f"Expected answers to all 8 questions; answered {answered!r}."
    )

    _wait_result_screen(driver, timeout=55)
    heading = _find_text(driver, RESULT_HEADINGS, exact=True)
    assert heading, "No win/loss/draw heading appeared on the result screen."
    _wait_text(driver, RESULT_CORRECT_LABELS, timeout=10)

    print(f"[GAME] PASS: answered {answered}; result={_text(heading)!r}.")


def test_game_05_result_screen_closes(driver):
    """Stage 5: click MENU and verify that the result screen closes."""
    _wait_result_screen(driver, timeout=20)
    heading = _find_text(driver, RESULT_HEADINGS, exact=True)
    assert heading, "The result heading is not visible."
    heading_text = _text(heading)

    menu = _scroll_to_text(driver, RESULT_MENU, attempts=10, exact=True)
    menu.click()

    # Only require the result screen to disappear.
    WebDriverWait(
        driver, 15, poll_frequency=0.3
    ).until(lambda current_driver: not _result_visible(current_driver))

    print(f"[GAME] PASS: result screen closed ({heading_text!r}).")
