"""Friends tests using shared helpers from test_navigation.py."""

import pytest
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait

from test_navigation import (
    RANKING_TEXT,
    FRIENDS_TEXT,
    _open_home,
    _tap_tab,
    _wait_text,
    _wait_ranking_loaded,
    _open_friends_hub,
    _scroll_to_text,
    _click_text,
    _wait_id,
    _id_elements,
    _visible,
    _text,
    _click_id,
    _position_friends_heading,
    _first_friend_target,
    _click_friend_row,
    _wait_friends_hub,
)

ADD_FRIEND = ("DODAJ ZNAJOMEGO", "Add Friend")
SENT_STATUS = ("Wysłano", "Sent")
REMOVE_TITLE = ("Usunąć znajomego?", "Remove friend?")


def test_friends_ranking_tab_opens(driver):
    """Test 1: Open Ranking and verify that it loads."""
    _open_home(driver)
    _tap_tab(driver, 1)

    _wait_text(driver, RANKING_TEXT, timeout=15, exact=True)
    _wait_text(driver, ("Świat", "World"), timeout=15, exact=True)
    _wait_text(driver, FRIENDS_TEXT, timeout=15, exact=True, index=0)
    _wait_ranking_loaded(driver)


def test_friends_send_invitation_to_first_available_suggestion(driver):
    """Test 2: Send an invitation to the first available suggestion."""
    _open_friends_hub(driver)

    _scroll_to_text(driver, ADD_FRIEND)
    _click_text(driver, ADD_FRIEND, timeout=12)

    _wait_id(driver, "search_friends_input", timeout=12)
    _wait_id(driver, "suggested_recycler_view", timeout=12)

    def first_available_button(current_driver):
        buttons = [
            element
            for element in current_driver.find_elements(
                AppiumBy.ID,
                "com.pandago.app:id/invite_button",
            )
            if _visible(element) and element.is_enabled()
        ]

        return (
            sorted(buttons, key=lambda element: element.rect["y"])[0]
            if buttons
            else False
        )

    try:
        button = WebDriverWait(
            driver, 10, poll_frequency=0.3
        ).until(first_available_button)
    except TimeoutException:
        pytest.skip("No available friend suggestions to invite.")

    button.click()

    # UserAdapter changes the button text to Wysłano/Sent after the tap.
    WebDriverWait(
        driver, 10, poll_frequency=0.3
    ).until(
        lambda current_driver: any(
            label.casefold() in _text(button).casefold()
            for label in SENT_STATUS
        )
    )

    assert not button.is_enabled(), (
        "The invitation button should be disabled after sending."
    )

    _click_id(driver, "btn_back", timeout=8)
    _wait_friends_hub(driver)


def test_friends_remove_first_available_friend(driver):
    """Test 3: Remove the first friend, or skip if the list is empty."""
    _open_friends_hub(driver)
    _position_friends_heading(driver)

    try:
        target = WebDriverWait(
            driver, 12, poll_frequency=0.3
        ).until(
            lambda current_driver: (
                _first_friend_target(current_driver) or False
            )
        )
    except TimeoutException:
        pytest.skip("No friends found in the list.")

    if target == "NO_FRIENDS":
        pytest.skip("No friends found in the list.")

    nickname = _text(target)
    assert nickname, "Could not read the friend's nickname."

    _click_friend_row(driver, target)
    _wait_id(driver, "remove_friend_button", timeout=12)
    _click_id(driver, "remove_friend_button", timeout=10)

    _wait_text(driver, REMOVE_TITLE, timeout=10, exact=True)
    _wait_id(driver, "cancel_button", timeout=8)
    _click_id(driver, "remove_button", timeout=8)

    # The app returns to Ranking after the removal succeeds.
    _wait_friends_hub(driver)
    _position_friends_heading(driver)

    def friend_removed(current_driver):
        return not any(
            _visible(element) and _text(element) == nickname
            for element in current_driver.find_elements(
                AppiumBy.XPATH, "//*[@text]"
            )
        )

    WebDriverWait(
        driver, 20, poll_frequency=0.5
    ).until(friend_removed)

    assert friend_removed(driver), (
        f"Friend {nickname!r} is still visible after removal."
    )
