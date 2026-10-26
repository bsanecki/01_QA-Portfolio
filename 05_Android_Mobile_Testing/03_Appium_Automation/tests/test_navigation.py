import base64
import queue
import re
import subprocess
import threading
import time

import pytest
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait

from config.settings import PANDAGO_APP_PACKAGE


HOME_TEXT = ("Wybierz tryb gry", "Choose game mode")
DUEL_TEXT = ("Pojedynek 1 vs 1", "1 vs 1 Duel")
FRIEND_MODE_TEXT = ("Gra z przyjacielem", "Play with Friend")
FREE_COINS_TEXT = ("Darmowe monety", "Darmowe Monety", "Free Coins")

REWARDS_TEXT = ("Nagrody", "Rewards")
WHEEL_LABEL = ("Koło Fortuny", "Lucky Wheel")
VIP_SHOP_LABEL = ("Sklep VIP", "VIP Shop")
TASKS_LABEL = ("Zadania", "Tasks")
WHEEL_TITLE = ("BAMBU FORTUNY", "LUCKY BAMBU")
WHEEL_FREE_SPIN_TEXT = ("DARMOWY SPIN CODZIENNIE!", "DAILY FREE SPIN!")
WHEEL_SPIN_TEXT = ("ZAKRĘĆ TERAZ!", "SPIN NOW!")
WHEEL_SPINNING_TEXT = ("LOSOWANIE...", "SPINNING...")
WHEEL_BACK_TEXT = ("POWRÓT", "BACK")
VIP_SCREEN_TEXT = ("VIP",)
VIP_EARN_MORE_TEXT = ("ZYSKAJ WIĘCEJ. GRAJ LEPIEJ.", "EARN MORE. PLAY BETTER.")
VIP_BACK_TEXT = ("POWRÓT DO MENU", "BACK TO MENU")

RANKING_TEXT = ("Ranking",)
WORLD_TEXT = ("Świat", "World")
FRIENDS_TEXT = ("Znajomi", "Friends")
FRIENDS_HUB_TEXT = ("Twój kod polecający", "Your referral code")
FRIENDS_HEADING = ("Twoi Znajomi", "Your Friends")
NO_FRIENDS_TEXT = ("Brak znajomych", "No friends")

BOTTOM_NAV_ID = f"{PANDAGO_APP_PACKAGE}:id/bottom_nav_compose_view"
CATEGORY_ID = f"{PANDAGO_APP_PACKAGE}:id/category_name"


def _visible(element):
    try:
        return element.is_displayed()
    except WebDriverException:
        return False


def _text(element):
    try:
        return (element.text or element.get_attribute("text") or "").strip()
    except WebDriverException:
        return ""


def _xpath_literal(value):
    if "'" not in value:
        return f"'{value}'"

    if '"' not in value:
        return f'"{value}"'

    parts = value.split("'")
    return "concat(" + ', "\'", '.join(
        f"'{part}'" for part in parts
    ) + ")"


def _text_elements(driver, labels, exact=False):
    found = {}

    for label in labels:
        literal = _xpath_literal(label)

        condition = (
            f"@text={literal}"
            if exact
            else f"contains(@text, {literal})"
        )

        for element in driver.find_elements(
            AppiumBy.XPATH,
            f"//*[@text and ({condition})]",
        ):
            if _visible(element):
                found[element.id] = element

    return sorted(
        found.values(),
        key=lambda element: (
            element.rect.get("y", 0),
            element.rect.get("x", 0),
        ),
    )


def _find_text(driver, labels, exact=False):
    elements = _text_elements(driver, labels, exact=exact)
    return elements[0] if elements else False


def _wait_text(driver, labels, timeout=20, exact=False, index=0):
    def locate(current_driver):
        elements = _text_elements(
            current_driver, labels, exact=exact
        )
        return elements[index] if len(elements) > index else False

    return WebDriverWait(
        driver, timeout, poll_frequency=0.3
    ).until(locate)


def _click_text(driver, labels, timeout=15, exact=False, index=0):
    element = _wait_text(
        driver,
        labels,
        timeout=timeout,
        exact=exact,
        index=index,
    )
    element.click()
    return element


def _rid(name):
    return f"{PANDAGO_APP_PACKAGE}:id/{name}"


def _id_elements(driver, name):
    return driver.find_elements(AppiumBy.ID, _rid(name))


def _id_visible(driver, name):
    return any(_visible(e) for e in _id_elements(driver, name))


def _wait_id(driver, name, timeout=12):
    return WebDriverWait(
        driver, timeout, poll_frequency=0.3
    ).until(
        lambda current_driver: next(
            (
                element
                for element in _id_elements(current_driver, name)
                if _visible(element)
            ),
            False,
        )
    )


def _click_id(driver, name, timeout=12):
    element = _wait_id(driver, name, timeout)
    element.click()
    return element


def _wait_id_hidden(driver, name, timeout=10):
    WebDriverWait(
        driver, timeout, poll_frequency=0.3
    ).until(
        lambda current_driver: not _id_visible(current_driver, name)
    )


def _tap_tab(driver, index):
    rect = _wait_id(driver, "bottom_nav_compose_view").rect

    driver.execute_script(
        "mobile: clickGesture",
        {
            "x": round(
                rect["x"] + rect["width"] * (index + 0.5) / 4
            ),
            "y": round(rect["y"] + rect["height"] / 2),
        },
    )


def _scroll_screen(driver, percent=0.58, direction="down"):
    size = driver.get_window_size()

    driver.execute_script(
        "mobile: scrollGesture",
        {
            "left": int(size["width"] * 0.05),
            "top": int(size["height"] * 0.14),
            "width": int(size["width"] * 0.90),
            "height": int(size["height"] * 0.68),
            "direction": direction,
            "percent": percent,
        },
    )


def _scroll_to_text(driver, labels, attempts=8, exact=False):
    height = driver.get_window_size()["height"]

    for _ in range(attempts):
        element = _find_text(driver, labels, exact=exact)

        if element:
            rect = element.rect

            if (
                rect["y"] >= 0
                and rect["y"] + rect["height"] < height * 0.84
            ):
                return element

        _scroll_screen(driver)

    return _wait_text(
        driver, labels, timeout=5, exact=exact
    )


def _open_home(driver):
    try:
        driver.terminate_app(PANDAGO_APP_PACKAGE)
    except WebDriverException:
        pass

    driver.activate_app(PANDAGO_APP_PACKAGE)
    _wait_text(driver, HOME_TEXT, timeout=30)
    _wait_id(driver, "bottom_nav_compose_view", timeout=15)


def _wait_rewards_screen(driver, timeout=15):
    """Wait until the Rewards page and its three action cards are visible."""
    _wait_text(driver, REWARDS_TEXT, timeout=timeout, exact=True)
    _wait_text(driver, WHEEL_LABEL, timeout=timeout, exact=True)
    _wait_text(driver, VIP_SHOP_LABEL, timeout=timeout, exact=True)
    _wait_text(driver, TASKS_LABEL, timeout=timeout, exact=True)
    return True


def _open_rewards(driver):
    """Open the third bottom-navigation tab (Rewards)."""
    _open_home(driver)
    _tap_tab(driver, 2)
    _wait_rewards_screen(driver, timeout=15)


def _click_rewards_card(driver, labels, card_index):
    """Tap the centre of one of the three horizontally arranged Rewards cards.

    Tapping the tile centre (instead of only its text label) makes the click
    hit the clickable parent Surface reliably in Jetpack Compose.
    card_index: 0 = Lucky Wheel, 1 = VIP Shop, 2 = Tasks.
    """
    if card_index not in (0, 1, 2):
        raise ValueError("card_index must be 0, 1, or 2")

    label = _scroll_to_text(driver, labels, attempts=3, exact=True)
    rect = label.rect
    screen = driver.get_window_size()

    # The actual cards have small horizontal padding/gaps; the thirds of the
    # screen still land safely inside the respective card on normal devices.
    x = round(screen["width"] * (card_index + 0.5) / 3)
    y = round(rect["y"] + rect["height"] / 2)

    driver.execute_script(
        "mobile: clickGesture",
        {"x": x, "y": y},
    )


def _wheel_cooldown_timer(driver):
    """Return a visible HH:MM:SS countdown, if the daily spin is unavailable."""
    for element in driver.find_elements(AppiumBy.XPATH, "//*[@text]"):
        if not _visible(element):
            continue
        value = _text(element)
        if re.fullmatch(r"\d{2}:\d{2}:\d{2}", value):
            return element
    return False


def _scroll_to_id(driver, name, attempts=8, direction="down"):
    """Scroll a native screen until the ID is within the visible viewport."""
    screen_height = driver.get_window_size()["height"]

    for _ in range(attempts):
        for element in _id_elements(driver, name):
            if not _visible(element):
                continue

            rect = element.rect
            if (
                rect["y"] >= 0
                and rect["y"] + rect["height"] < screen_height * 0.92
            ):
                return element

        _scroll_screen(driver, percent=0.65, direction=direction)

    return _wait_id(driver, name, timeout=5)


def _open_mode(driver, labels):
    _open_home(driver)
    _click_text(driver, labels)

    def categories_loaded(current_driver):
        categories = [
            element
            for element in current_driver.find_elements(
                AppiumBy.ID, CATEGORY_ID
            )
            if _visible(element) and _text(element)
        ]
        return categories if len(categories) >= 2 else False

    categories = WebDriverWait(
        driver, 15, poll_frequency=0.3
    ).until(categories_loaded)

    assert len(categories) >= 2


def _back_to_home_from_game(driver):
    _click_id(driver, "back_button_game", timeout=10)
    _wait_text(driver, HOME_TEXT, timeout=15)
    _wait_id(driver, "bottom_nav_compose_view", timeout=10)


def _wait_ranking_loaded(driver):
    return _wait_text(
        driver,
        ("Nowy ranking za:", "New ranking in:"),
        timeout=25,
    )


def _open_ranking(driver):
    _open_home(driver)
    _tap_tab(driver, 1)

    _wait_text(driver, RANKING_TEXT, timeout=15, exact=True)
    _wait_text(driver, WORLD_TEXT, timeout=15, exact=True)
    _wait_text(
        driver, FRIENDS_TEXT, timeout=15, exact=True, index=0
    )
    _wait_ranking_loaded(driver)


def _open_friends_hub(driver):
    _open_ranking(driver)
    _click_text(
        driver, FRIENDS_TEXT, exact=True, index=0
    )
    _wait_text(driver, FRIENDS_HUB_TEXT, timeout=20)


def _wait_friends_hub(driver):
    # Returning from FriendInviteFragment or PublicProfileFragment can recreate
    # RankingFragment and reset its selected main tab to "Ranking".
    # Restore the top-level "Znajomi" tab before checking the Friends Hub.
    if _find_text(driver, FRIENDS_HUB_TEXT):
        return _wait_text(driver, FRIENDS_HUB_TEXT, timeout=15)

    if _find_text(driver, RANKING_TEXT, exact=True):
        _click_text(
            driver,
            FRIENDS_TEXT,
            timeout=10,
            exact=True,
            index=0,
        )

    return _wait_text(driver, FRIENDS_HUB_TEXT, timeout=15)


def _find_referral_code(driver, timeout=20):
    pattern = re.compile(
        r"\b[A-Z0-9]{1,8}-[A-Z0-9]{3,6}\b",
        re.IGNORECASE,
    )

    def locate(current_driver):
        heading = _find_text(
            current_driver, FRIENDS_HUB_TEXT
        )

        if not heading:
            return False

        heading_y = heading.rect["y"]
        max_y = (
            heading_y
            + current_driver.get_window_size()["height"] * 0.22
        )

        candidates = []

        for element in current_driver.find_elements(
            AppiumBy.XPATH, "//*[@text]"
        ):
            if not _visible(element):
                continue

            value = _text(element)
            match = pattern.search(value)

            if not match:
                continue

            y = element.rect["y"]

            if heading_y - 20 <= y <= max_y:
                candidates.append(
                    (abs(y - heading_y), element, match.group(0))
                )

        if candidates:
            _, element, code = min(
                candidates, key=lambda item: item[0]
            )
            return element, code

        return False

    return WebDriverWait(
        driver, timeout, poll_frequency=0.3
    ).until(locate)


def _click_copy_control(driver, code_element):
    rect = code_element.rect
    right = rect["x"] + rect["width"]
    center_y = rect["y"] + rect["height"] / 2
    candidates = []

    for element in driver.find_elements(
        AppiumBy.XPATH, "//*[@clickable='true']"
    ):
        if not _visible(element):
            continue

        item = element.rect
        item_y = item["y"] + item["height"] / 2
        gap = item["x"] - right

        if -8 <= gap <= 240 and abs(item_y - center_y) <= 100:
            score = abs(item_y - center_y) + abs(max(gap, 0)) * 0.1
            candidates.append((score, element))

    assert candidates, (
        "The referral-code copy control was not exposed as clickable."
    )

    min(candidates, key=lambda item: item[0])[1].click()


def _clipboard_text(driver):
    value = driver.get_clipboard()

    if isinstance(value, bytes):
        value = value.decode("utf-8", errors="replace")

    value = str(value or "")

    try:
        decoded = base64.b64decode(value, validate=True).decode("utf-8")
        return decoded if decoded else value
    except (ValueError, UnicodeDecodeError):
        return value


def _wait_for_share_chooser(driver, timeout=12):
    markers = (
        "Bluetooth",
        "Gmail",
        "Nearby Share",
        "Kopiuj",
        "Copy",
        "Messages",
        "Wiadomości",
    )

    def chooser_opened(current_driver):
        try:
            if current_driver.current_package != PANDAGO_APP_PACKAGE:
                return True
        except WebDriverException:
            return False

        return bool(_find_text(current_driver, markers))

    WebDriverWait(
        driver, timeout, poll_frequency=0.3
    ).until(chooser_opened)


def _open_invitation_sheet(driver, card_labels, expected_title):
    _open_friends_hub(driver)
    _scroll_to_text(driver, card_labels)
    _click_text(driver, card_labels)

    title = _wait_id(driver, "sheet_title", timeout=12)

    assert expected_title.casefold() in _text(title).casefold(), (
        f"Expected sheet title containing {expected_title!r}; "
        f"got {_text(title)!r}."
    )

    def sheet_loaded(current_driver):
        # An empty invitation list hides the RecyclerView. Wait for either
        # the list or the empty-state view, but not while loading is visible.
        if _id_visible(current_driver, "sheet_loading"):
            return False

        return (
            _id_visible(current_driver, "invitations_recycler_view")
            or _id_visible(current_driver, "empty_state_container")
        )

    WebDriverWait(
        driver, 20, poll_frequency=0.3
    ).until(sheet_loaded)

    _click_id(driver, "btn_close_sheet", timeout=10)
    _wait_id_hidden(driver, "sheet_title", timeout=10)
    _wait_friends_hub(driver)


def _start_ad_logcat(driver):
    capabilities = driver.capabilities

    device_id = (
        capabilities.get("udid")
        or capabilities.get("appium:udid")
        or capabilities.get("deviceUDID")
    )

    adb = ["adb"]

    if device_id:
        adb.extend(["-s", str(device_id)])

    subprocess.run(
        adb + ["logcat", "-c"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        timeout=5,
        check=False,
    )

    process = subprocess.Popen(
        adb + ["logcat", "-v", "brief", "AdsManager:V", "*:S"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    messages = queue.Queue()

    def read_logs():
        if process.stdout is not None:
            for line in iter(process.stdout.readline, ""):
                messages.put(line.rstrip())

    threading.Thread(target=read_logs, daemon=True).start()

    return process, messages


def _wait_for_log(messages, expected, history, timeout=60):
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        try:
            line = messages.get(
                timeout=min(
                    0.5,
                    max(0.1, deadline - time.monotonic()),
                )
            )
        except queue.Empty:
            continue

        history.append(line)

        if expected in line:
            return line

    pytest.fail(
        f"Expected log message was not found: {expected!r}\n"
        + "\n".join(history[-20:])
    )


def _first_friend_target(driver):
    """Find a visible friend name below the Friends heading."""
    heading = _find_text(driver, FRIENDS_HEADING, exact=True)

    if not heading:
        return False

    heading_bottom = heading.rect["y"] + heading.rect["height"]

    nav_top = (
        _wait_id(driver, "bottom_nav_compose_view").rect["y"]
        if _id_visible(driver, "bottom_nav_compose_view")
        else driver.get_window_size()["height"]
    )

    ignored = {
        "twoi znajomi", "your friends", "brak znajomych", "no friends",
        "dodaj znajomego", "add friend", "zaproszenia", "invitations",
        "wysłane", "sent", "wysłane zaproszenia", "sent invitations",
        "udostępnij", "share",
    }

    elements = [
        e for e in driver.find_elements(AppiumBy.XPATH, "//*[@text]")
        if _visible(e) and _text(e)
    ]

    empty_labels = {label.casefold() for label in NO_FRIENDS_TEXT}

    for element in elements:
        rect = element.rect
        if (
            _text(element).casefold() in empty_labels
            and heading_bottom < rect["y"] < nav_top
        ):
            return "NO_FRIENDS"

    candidates = []

    for element in elements:
        value = _text(element).strip()
        rect = element.rect

        if not (heading_bottom < rect["y"] < nav_top):
            continue

        if value.casefold() in ignored:
            continue

        if re.fullmatch(r"[\d\s.,🏆⭐]+", value):
            continue

        candidates.append(element)

    if not candidates:
        return False

    return sorted(
        candidates,
        key=lambda e: (e.rect["y"], e.rect["x"]),
    )[0]


def _friend_profile_is_open(driver):
    return all(
        _id_visible(driver, item)
        for item in ("profile_image", "nickname_text", "ranking_points_text")
    )


def _click_friend_row(driver, target):
    """Tap the full-width clickable friend card, not just its text label."""
    rect = target.rect
    screen = driver.get_window_size()
    y = round(rect["y"] + rect["height"] / 2)

    try:
        ancestors = target.find_elements(
            AppiumBy.XPATH,
            "ancestor-or-self::*[@clickable='true']",
        )
    except WebDriverException:
        ancestors = []

    rows = [
        element
        for element in ancestors
        if _visible(element)
        and element.rect["width"] >= screen["width"] * 0.65
        and element.rect["height"] >= max(40, rect["height"] * 1.5)
        and element.rect["height"] <= screen["height"] * 0.25
    ]

    for row in sorted(rows, key=lambda element: element.rect["height"]):
        try:
            row.click()

            WebDriverWait(
                driver, 2, poll_frequency=0.2
            ).until(_friend_profile_is_open)

            return
        except (TimeoutException, WebDriverException):
            pass

    driver.execute_script(
        "mobile: clickGesture",
        {
            "x": round(screen["width"] / 2),
            "y": y,
        },
    )

    try:
        WebDriverWait(
            driver, 5, poll_frequency=0.2
        ).until(_friend_profile_is_open)
    except TimeoutException:
        target.click()

        WebDriverWait(
            driver, 8, poll_frequency=0.2
        ).until(_friend_profile_is_open)


def _position_friends_heading(driver):
    heading = _scroll_to_text(
        driver, FRIENDS_HEADING, attempts=8, exact=True
    )

    height = driver.get_window_size()["height"]

    for _ in range(8):
        heading = _find_text(driver, FRIENDS_HEADING, exact=True)

        if heading and heading.rect["y"] <= height * 0.25:
            return heading

        _scroll_screen(driver, percent=0.45)

    return _wait_text(
        driver, FRIENDS_HEADING, timeout=8, exact=True
    )


# ---------------------------------------------------------------------------
# Navigation and Friends tests
# ---------------------------------------------------------------------------

def test_app_opens_on_home_screen(driver):
    _open_home(driver)
    assert _find_text(driver, HOME_TEXT)


def test_duel_1vs1_opens_and_returns_to_home(driver):
    _open_mode(driver, DUEL_TEXT)
    _back_to_home_from_game(driver)
    assert _find_text(driver, HOME_TEXT)


def test_play_with_friends_opens_and_returns_to_home(driver):
    _open_mode(driver, FRIEND_MODE_TEXT)
    _back_to_home_from_game(driver)
    assert _find_text(driver, HOME_TEXT)


@pytest.mark.skip(reason="Daily Quiz is not implemented yet.")
def test_daily_quiz_is_not_implemented_yet():
    pass


def test_free_coins_rewarded_ad_loads_and_opens(driver):
    process = None
    history = []

    try:
        process, messages = _start_ad_logcat(driver)
        _open_home(driver)

        _wait_for_log(
            messages,
            "Rewarded ad loaded successfully",
            history,
            timeout=60,
        )

        _click_text(driver, FREE_COINS_TEXT, timeout=15)

        _wait_for_log(
            messages,
            "showRewarded called",
            history,
            timeout=12,
        )

        time.sleep(5)

    finally:
        try:
            driver.terminate_app(PANDAGO_APP_PACKAGE)
        except WebDriverException:
            pass

        if process is not None:
            process.terminate()

            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()


def test_ranking_subtabs_world_friends_and_main_tabs_switch(driver):
    _open_ranking(driver)

    world_selected = _wait_text(
        driver, WORLD_TEXT, exact=True
    ).screenshot_as_png

    _click_text(driver, FRIENDS_TEXT, exact=True, index=1)
    _wait_ranking_loaded(driver)
    time.sleep(0.4)

    world_unselected = _wait_text(
        driver, WORLD_TEXT, exact=True
    ).screenshot_as_png

    assert world_unselected != world_selected, (
        "The World subtab did not visibly change its selected state."
    )

    _click_text(driver, WORLD_TEXT, exact=True)
    _wait_ranking_loaded(driver)
    time.sleep(0.4)

    world_selected_again = _wait_text(
        driver, WORLD_TEXT, exact=True
    ).screenshot_as_png

    assert world_selected_again != world_unselected, (
        "The World subtab did not become selected again."
    )

    _click_text(driver, FRIENDS_TEXT, exact=True, index=0)
    _wait_text(driver, FRIENDS_HUB_TEXT, timeout=20)

    _click_text(driver, RANKING_TEXT, exact=True)
    _wait_ranking_loaded(driver)

    _wait_text(driver, WORLD_TEXT, exact=True)
    _wait_text(driver, FRIENDS_TEXT, exact=True)


def test_friends_referral_code_copy_matches_clipboard(driver):
    _open_friends_hub(driver)

    code_element, referral_code = _find_referral_code(driver)
    _click_copy_control(driver, code_element)

    WebDriverWait(
        driver, 8, poll_frequency=0.3
    ).until(
        lambda current_driver: (
            referral_code in _clipboard_text(current_driver)
        )
    )

    assert referral_code in _clipboard_text(driver)


def test_friends_share_opens_share_chooser_and_returns(driver):
    _open_friends_hub(driver)

    _click_text(driver, ("Udostępnij", "Share"), exact=True)
    _wait_for_share_chooser(driver, timeout=12)

    driver.back()
    _wait_friends_hub(driver)

    assert _find_text(driver, FRIENDS_HUB_TEXT)


def test_add_friend_screen_opens_and_returns(driver):
    _open_friends_hub(driver)

    _scroll_to_text(
        driver,
        ("DODAJ ZNAJOMEGO", "Add Friend"),
    )

    _click_text(
        driver,
        ("DODAJ ZNAJOMEGO", "Add Friend"),
    )

    _wait_id(driver, "search_friends_input", timeout=15)
    _wait_id(driver, "suggested_recycler_view", timeout=15)
    _wait_id(driver, "section_title", timeout=12)

    _click_id(driver, "btn_back", timeout=10)
    _wait_friends_hub(driver)

    assert _find_text(driver, FRIENDS_HUB_TEXT)


def test_received_invitations_sheet_opens_and_closes(driver):
    _open_invitation_sheet(
        driver,
        ("Zaproszenia", "Invitations"),
        "Zaproszenia",
    )


def test_sent_invitations_sheet_opens_and_closes(driver):
    _open_invitation_sheet(
        driver,
        ("Wysłane", "Sent"),
        "Wysłane zaproszenia",
    )


def test_first_friend_profile_opens_and_returns(driver):
    _open_friends_hub(driver)
    _position_friends_heading(driver)

    target = WebDriverWait(
        driver, 20, poll_frequency=0.3
    ).until(
        lambda current_driver: (
            _first_friend_target(current_driver)
            or False
        )
    )

    if target == "NO_FRIENDS":
        pytest.skip("No friends available")

    _click_friend_row(driver, target)

    _wait_id(driver, "profile_image", timeout=10)
    _wait_id(driver, "nickname_text", timeout=10)
    _wait_id(driver, "ranking_points_text", timeout=10)

    nickname = _text(
        _wait_id(driver, "nickname_text", timeout=10)
    )

    assert nickname, "The friend's profile has no nickname."

    _click_id(driver, "back_button", timeout=10)
    _wait_friends_hub(driver)

    assert _find_text(driver, FRIENDS_HUB_TEXT)


# ---------------------------------------------------------------------------
# Rewards tab tests
# ---------------------------------------------------------------------------

def test_rewards_tab_opens_and_shows_three_options(driver):
    """Open the third bottom tab and verify Wheel, VIP Shop, and Tasks."""
    _open_rewards(driver)

    assert _find_text(driver, REWARDS_TEXT, exact=True)
    assert _find_text(driver, WHEEL_LABEL, exact=True)
    assert _find_text(driver, VIP_SHOP_LABEL, exact=True)
    assert _find_text(driver, TASKS_LABEL, exact=True)


def test_rewards_lucky_wheel_opens_and_returns(driver):
    """Open Lucky Wheel, verify the screen, and return to Rewards."""
    _open_rewards(driver)
    _click_rewards_card(driver, WHEEL_LABEL, card_index=0)

    _wait_text(driver, WHEEL_TITLE, timeout=15, exact=True)
    _wait_text(driver, WHEEL_FREE_SPIN_TEXT, timeout=10)

    back_button = _scroll_to_text(
        driver, WHEEL_BACK_TEXT, attempts=10, exact=True
    )
    back_button.click()
    _wait_rewards_screen(driver, timeout=15)


def test_rewards_lucky_wheel_spin_attempt(driver):
    """Attempt the daily spin; skip if the 24-hour cooldown is active."""
    _open_rewards(driver)
    _click_rewards_card(driver, WHEEL_LABEL, card_index=0)

    _wait_text(driver, WHEEL_TITLE, timeout=15, exact=True)
    _wait_text(driver, WHEEL_FREE_SPIN_TEXT, timeout=10)

    # Wait for asynchronous cooldown state from the app/backend.
    time.sleep(5)

    timer = _wheel_cooldown_timer(driver)
    spin_button = _find_text(driver, WHEEL_SPIN_TEXT, exact=True)

    if timer and not spin_button:
        pytest.skip(
            "Lucky Wheel is unavailable because the 24-hour cooldown is active. "
            f"Time remaining: {_text(timer)}."
        )

    if not spin_button:
        WebDriverWait(
            driver, 12, poll_frequency=0.3
        ).until(
            lambda current_driver: (
                _wheel_cooldown_timer(current_driver)
                or _find_text(
                    current_driver,
                    WHEEL_SPIN_TEXT,
                    exact=True,
                )
            )
        )

        timer = _wheel_cooldown_timer(driver)
        spin_button = _find_text(
            driver, WHEEL_SPIN_TEXT, exact=True
        )

        if timer and not spin_button:
            pytest.skip(
                "Lucky Wheel is unavailable because the 24-hour cooldown is active. "
                f"Time remaining: {_text(timer)}."
            )

    assert spin_button, (
        "No active spin button or cooldown timer was found. "
    )

    rect = spin_button.rect

    driver.execute_script(
        "mobile: clickGesture",
        {
            "x": round(rect["x"] + rect["width"] / 2),
            "y": round(rect["y"] + rect["height"] / 2),
        },
    )

    WebDriverWait(
        driver, 10, poll_frequency=0.3
    ).until(
        lambda current_driver: (
            _find_text(
                current_driver, WHEEL_SPINNING_TEXT, exact=True
            )
            or _wheel_cooldown_timer(current_driver)
        )
    )

    # A successful spin should enable the next-spin countdown.
    WebDriverWait(
        driver, 20, poll_frequency=0.3
    ).until(
        lambda current_driver: (
            _wheel_cooldown_timer(current_driver) or False
        )
    )


def test_rewards_vip_shop_opens_and_returns(driver):
    """Open the VIP shop and return to Rewards without purchasing."""
    _open_rewards(driver)
    _click_rewards_card(driver, VIP_SHOP_LABEL, card_index=1)

    _wait_text(driver, VIP_SCREEN_TEXT, timeout=15, exact=True)
    _wait_text(driver, VIP_EARN_MORE_TEXT, timeout=10)

    back_button = _scroll_to_text(
        driver, VIP_BACK_TEXT, attempts=10, exact=True
    )
    back_button.click()

    _wait_rewards_screen(driver, timeout=15)


def test_rewards_tasks_opens_and_returns(driver):
    """Open Daily Tasks, verify both task sections, and return to Rewards."""
    _open_rewards(driver)
    _click_rewards_card(driver, TASKS_LABEL, card_index=2)

    daily_title = _wait_id(driver, "title_daily_tasks", timeout=15)
    _wait_id(driver, "daily_tasks_recycler_view", timeout=15)

    assert (
        "zadania codzienne" in _text(daily_title).casefold()
        or "daily tasks" in _text(daily_title).casefold()
    ), f"Unexpected daily tasks heading: {_text(daily_title)!r}"

    other_title = _scroll_to_id(
        driver, "title_other_tasks", attempts=10, direction="down"
    )
    other_tasks_list = _scroll_to_id(
        driver, "other_tasks_recycler_view", attempts=5, direction="down"
    )

    assert other_title and other_tasks_list
    assert (
        "wyzwania" in _text(other_title).casefold()
        or "challenges" in _text(other_title).casefold()
    ), f"Unexpected other tasks heading: {_text(other_title)!r}"

    back_button = _scroll_to_id(
        driver, "btn_back", attempts=10, direction="up"
    )
    back_button.click()

    _wait_rewards_screen(driver, timeout=15)

# ---------------------------------------------------------------------------
# Profile tab tests
# ---------------------------------------------------------------------------

PROFILE_SECTION_PL = ("Twoje dane",)
PROFILE_SECTION_EN = ("Your Data",)
ACHIEVEMENTS_TITLE = ("MOJE OSIĄGNIĘCIA", "MY ACHIEVEMENTS")
NICKNAME_NOT_SET = ("Nie ustawiono", "Not set")


def _open_profile(driver):
    """Open the fourth bottom-navigation tab and wait for profile data."""
    _open_home(driver)
    _tap_tab(driver, 3)

    _wait_id(driver, "profile_image", timeout=20)
    _wait_id(driver, "nickname_text", timeout=20)
    _wait_id(driver, "edit_nickname_button", timeout=15)

    return True


def _open_avatar_picker(driver):
    _click_id(driver, "profile_image", timeout=12)

    _wait_id(driver, "title", timeout=10)
    _wait_id(driver, "categories_recycler_mock", timeout=10)
    _wait_id(driver, "avatars_grid_recycler_mock", timeout=10)


def _close_avatar_picker(driver):
    driver.back()

    _wait_id_hidden(driver, "title", timeout=10)
    _wait_id(driver, "profile_image", timeout=10)


def _profile_button(driver, resource_id):
    """Scroll a Profile option into view and click it by its source ID."""
    _scroll_to_id(driver, resource_id, attempts=12, direction="down")
    return _click_id(driver, resource_id, timeout=10)


def _open_nickname_dialog(driver):
    _scroll_to_id(driver, "edit_nickname_button", attempts=10)
    _click_id(driver, "edit_nickname_button", timeout=10)

    return _wait_id(driver, "nickname_edit_text", timeout=10)


def _enter_and_save_nickname(driver, nickname, dialog_timeout=6):
    """Return False for a nickname rejected by the uniqueness validation."""
    edit = _wait_id(driver, "nickname_edit_text", timeout=8)
    edit.click()
    edit.clear()
    edit.send_keys(nickname)

    try:
        driver.hide_keyboard()
    except WebDriverException:
        pass

    _click_id(driver, "save_button", timeout=8)

    try:
        WebDriverWait(
            driver, dialog_timeout, poll_frequency=0.3
        ).until(
            lambda current_driver: not _id_visible(
                current_driver, "nickname_edit_text"
            )
        )
    except TimeoutException:
        # The dialog remains open for invalid or already-taken nicknames.
        return False

    WebDriverWait(
        driver, 12, poll_frequency=0.3
    ).until(
        lambda current_driver: (
            _text(
                _wait_id(
                    current_driver, "nickname_text", timeout=2
                )
            ) == nickname
        )
    )

    return True


def _wait_external_activity(driver, timeout=12):
    """Wait until Android has opened an external app/chooser/browser."""
    def external_opened(current_driver):
        try:
            if current_driver.current_package != PANDAGO_APP_PACKAGE:
                return True
        except WebDriverException:
            return False

        return bool(
            _find_text(
                current_driver,
                (
                    "Gmail",
                    "Chrome",
                    "Bluetooth",
                    "Kopiuj",
                    "Copy",
                    "Wyślij e-mail przez",
                    "Open with",
                    "Open in browser",
                ),
            )
        )

    WebDriverWait(
        driver, timeout, poll_frequency=0.3
    ).until(external_opened)


def _select_profile_language(driver, language):
    """Select Polski or English, then wait for the locale recreation."""
    if language not in ("Polski", "English"):
        raise ValueError("language must be 'Polski' or 'English'")

    _open_profile(driver)
    _profile_button(driver, "language_button")
    _wait_id(driver, "language_recycler_view", timeout=12)

    _click_text(driver, (language,), timeout=10, exact=True)

    expected_home = (
        ("Wybierz tryb gry",)
        if language == "Polski"
        else ("Choose game mode",)
    )

    expected_profile = (
        PROFILE_SECTION_PL
        if language == "Polski"
        else PROFILE_SECTION_EN
    )

    WebDriverWait(
        driver, 25, poll_frequency=0.3
    ).until(
        lambda current_driver: (
            _find_text(current_driver, expected_home, exact=True)
            or _find_text(current_driver, expected_profile, exact=True)
        )
    )


def test_profile_tab_and_avatar_picker_open_and_close(driver):
    """Open Profile, open the avatar picker, and dismiss it without changes."""
    _open_profile(driver)

    _open_avatar_picker(driver)
    assert _find_text(driver, ("Profilowe",), exact=True)

    _close_avatar_picker(driver)

    assert _id_visible(driver, "profile_image")
    assert _id_visible(driver, "nickname_text")


def test_profile_avatar_can_be_changed(driver):
    """Choose a different avatar and verify the profile image changes."""
    _open_profile(driver)

    original_image = _wait_id(
        driver, "profile_image", timeout=10
    ).screenshot_as_png

    max_attempts = 8

    for index in range(max_attempts):
        if not _id_visible(driver, "title"):
            _open_avatar_picker(driver)

        tiles = [
            element
            for element in _id_elements(driver, "avatar_tile")
            if _visible(element)
        ]

        tiles.sort(
            key=lambda element: (
                element.rect.get("y", 0),
                element.rect.get("x", 0),
            )
        )

        if index >= len(tiles):
            pytest.fail(
                "Not enough avatar tiles were found to select a different profile picture. "

            )

        tile = tiles[index]
        rect = tile.rect

        driver.execute_script(
            "mobile: clickGesture",
            {
                "x": round(rect["x"] + rect["width"] / 2),
                "y": round(rect["y"] + rect["height"] / 2),
            },
        )

        _wait_id_hidden(driver, "title", timeout=10)

        try:
            WebDriverWait(
                driver, 6, poll_frequency=0.3
            ).until(
                lambda current_driver: (
                    _wait_id(
                        current_driver, "profile_image", timeout=2
                    ).screenshot_as_png != original_image
                )
            )

            assert (
                _wait_id(
                    driver, "profile_image", timeout=5
                ).screenshot_as_png != original_image
            ), "The avatar did not change after selecting a different image."

            return

        except TimeoutException:
            # It may have selected the currently active avatar. Reopen the
            # picker and try the next tile from the same category.
            continue

    pytest.fail(
        "The profile picture did not change after trying the available avatars."
    )


def test_profile_achievements_open_and_return(driver):
    """Open Achievements and return to the Profile tab."""
    _open_profile(driver)
    _profile_button(driver, "achievements_button")

    _wait_id(driver, "achievements_recycler_view", timeout=15)
    _wait_id(driver, "btn_back", timeout=10)
    _wait_text(driver, ACHIEVEMENTS_TITLE, timeout=12, exact=True)

    _click_id(driver, "btn_back", timeout=10)

    _wait_id(driver, "profile_image", timeout=15)
    _wait_id(driver, "nickname_text", timeout=10)

    assert _id_visible(driver, "edit_nickname_button")


def test_profile_nickname_changes_to_temporary_value_and_restores(driver):
    """Try a unique Tester nickname, verify it, and restore the original name."""
    _open_profile(driver)

    original = _text(
        _wait_id(driver, "nickname_text", timeout=10)
    )

    if not original or original.casefold() in {
        value.casefold() for value in NICKNAME_NOT_SET
    }:
        pytest.skip("No nickname is set to restore.")

    temporary_name = None

    try:
        input_element = _open_nickname_dialog(driver)

        assert (
            _text(input_element) == original
            or input_element.get_attribute("text") == original
        )

        # Try several names in case a candidate is already taken globally.
        candidates = [
            f"Tester{number:03d}"
            for number in range(1, 11)
        ]
        candidates = [
            candidate
            for candidate in candidates
            if candidate != original
        ]

        for candidate in candidates:
            if _enter_and_save_nickname(
                driver, candidate, dialog_timeout=6
            ):
                temporary_name = candidate
                break

        assert temporary_name, (
            "Could not save any test nickname from Tester001–Tester010. "

        )

        assert _text(
            _wait_id(driver, "nickname_text", timeout=10)
        ) == temporary_name

    finally:
        if temporary_name:
            _open_profile(driver)
            _open_nickname_dialog(driver)

            restored = _enter_and_save_nickname(
                driver, original, dialog_timeout=10
            )

            assert restored, (
                "Could not restore the original nickname."
            )

            assert _text(
                _wait_id(driver, "nickname_text", timeout=10)
            ) == original

        elif _id_visible(driver, "nickname_edit_text"):
            # No test name was accepted; close the still-open dialog safely.
            if _id_visible(driver, "cancel_button"):
                _click_id(driver, "cancel_button", timeout=5)


def test_profile_nationality_can_be_changed(driver):
    """Select a different visible country without using the search field."""
    _open_profile(driver)

    nationality_element = _wait_id(
        driver, "nationality_text", timeout=10
    )
    original = _text(nationality_element)

    def normalize_country(value):
        # Ignore spacing, punctuation, and flag emojis when comparing names.
        return "".join(
            char.casefold() for char in value if char.isalpha()
        )

    original_normalized = normalize_country(original)

    _profile_button(driver, "edit_nationality_button")
    country_list = _wait_id(
        driver, "countries_recycler_view", timeout=12
    )
    list_rect = country_list.rect

    def find_another_country(current_driver):
        candidates = []

        for element in current_driver.find_elements(
            AppiumBy.XPATH, "//*[@text]"
        ):
            if not _visible(element):
                continue

            value = _text(element).strip()
            normalized = normalize_country(value)

            # Ignore the current country. Do not search or type anything.
            if not normalized or normalized == original_normalized:
                continue

            rect = element.rect
            center_x = rect["x"] + rect["width"] / 2
            center_y = rect["y"] + rect["height"] / 2

            inside_list = (
                list_rect["x"] <= center_x
                <= list_rect["x"] + list_rect["width"]
                and list_rect["y"] <= center_y
                <= list_rect["y"] + list_rect["height"]
            )

            if inside_list:
                candidates.append(
                    (rect["y"], element, value, normalized)
                )

        if not candidates:
            return False

        candidates.sort(key=lambda item: item[0])
        return candidates[0]

    target_y, target_element, target_label, target_normalized = WebDriverWait(
        driver, 12, poll_frequency=0.3
    ).until(find_another_country)

    # Tap the alternative country directly; do not type into search.
    target_rect = target_element.rect

    driver.execute_script(
        "mobile: clickGesture",
        {
            "x": round(list_rect["x"] + list_rect["width"] / 2),
            "y": round(target_rect["y"] + target_rect["height"] / 2),
        },
    )

    def nationality_changed(current_driver):
        elements = _id_elements(current_driver, "nationality_text")

        for element in elements:
            if not _visible(element):
                continue

            new_value = _text(element)
            new_normalized = normalize_country(new_value)

            if new_normalized and new_normalized != original_normalized:
                return new_value

        return False

    changed_nationality = WebDriverWait(
        driver, 15, poll_frequency=0.3
    ).until(nationality_changed)

    assert normalize_country(changed_nationality) != original_normalized, (
        f"Nationality did not change. Original: {original!r}; "
        f"current: {changed_nationality!r}."
    )

    print(
        f"Nationality changed successfully: {original!r} -> "
        f"{changed_nationality!r} (selected row: {target_label!r})"
    )

def test_profile_gender_can_be_changed(driver):
    """Choose a gender different from the currently displayed value."""
    _open_profile(driver)

    current = _text(
        _wait_id(driver, "gender_text", timeout=10)
    ).casefold()

    target_labels = (
        ("Mężczyzna", "Male")
        if ("kobieta" in current or "female" in current)
        else ("Kobieta", "Female")
    )

    _profile_button(driver, "edit_gender_button")
    _wait_id(driver, "gender_recycler_view", timeout=12)

    _click_text(driver, target_labels, timeout=10, exact=True)

    WebDriverWait(
        driver, 15, poll_frequency=0.3
    ).until(
        lambda current_driver: (
            _text(
                _wait_id(
                    current_driver, "gender_text", timeout=2
                )
            ).casefold()
            in {label.casefold() for label in target_labels}
        )
    )

    assert _text(
        _wait_id(driver, "gender_text", timeout=10)
    ).casefold() in {
        label.casefold() for label in target_labels
    }


def test_profile_language_switches_to_english_and_restores_polish(driver):
    """Switch the app to English, verify it, then restore Polish."""
    try:
        _select_profile_language(driver, "English")
        _open_profile(driver)

        assert _find_text(
            driver, PROFILE_SECTION_EN, exact=True
        ), (
            "After switching to English, the profile heading is still not in English."
        )

    finally:
        # Always restore Polish, including when an assertion above fails.
        _select_profile_language(driver, "Polski")
        _open_profile(driver)

        assert _find_text(
            driver, PROFILE_SECTION_PL, exact=True
        ), "Could not restore the app language to Polish."


def test_profile_help_opens_email_chooser_and_returns(driver):
    """Open Help's email chooser and return to the Profile screen."""
    _open_profile(driver)
    _profile_button(driver, "help_button")
    _wait_external_activity(driver, timeout=12)

    driver.back()
    _wait_id(driver, "profile_image", timeout=15)

    assert _id_visible(driver, "help_button") or _find_text(
        driver, ("Pomoc", "Help"), exact=True
    )


def test_profile_privacy_policy_opens_and_returns(driver):
    """Open the Privacy Policy URL externally and return to Profile."""
    _open_profile(driver)
    _profile_button(driver, "privacy_policy_button")
    _wait_external_activity(driver, timeout=15)

    driver.back()
    _wait_id(driver, "profile_image", timeout=15)

    assert _id_visible(
        driver, "privacy_policy_button"
    ) or _find_text(
        driver, ("Polityka Prywatności", "Privacy Policy"), exact=True
    )


def test_profile_terms_open_and_return(driver):
    """Open the Terms link externally and return to Profile."""
    _open_profile(driver)
    _profile_button(driver, "terms_button")
    _wait_external_activity(driver, timeout=15)

    driver.back()
    _wait_id(driver, "profile_image", timeout=15)

    assert _id_visible(
        driver, "terms_button"
    ) or _find_text(
        driver, ("Regulamin", "Terms and Conditions"), exact=True
    )


def test_profile_delete_account_confirmation_can_be_cancelled(driver):
    """Open delete-account confirmation and cancel; never confirm deletion."""
    _open_profile(driver)
    _profile_button(driver, "delete_account_button")

    _wait_text(
        driver,
        ("Usunąć konto?", "Delete account?"),
        timeout=12,
        exact=True,
    )

    _wait_id(driver, "btn_confirm_delete", timeout=10)
    _wait_id(driver, "btn_cancel_delete", timeout=10)

    # Deliberately cancel. Never click btn_confirm_delete in automation.
    _click_id(driver, "btn_cancel_delete", timeout=10)

    _wait_id_hidden(driver, "btn_cancel_delete", timeout=10)
    _wait_id(driver, "profile_image", timeout=12)

    assert _id_visible(
        driver, "delete_account_button"
    ) or _find_text(
        driver, ("Usuń konto", "Delete account"), exact=True
    )
