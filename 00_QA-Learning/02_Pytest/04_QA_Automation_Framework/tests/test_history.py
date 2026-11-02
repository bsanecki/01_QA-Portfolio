from datetime import datetime

import pytest

from app.history import CalculationHistory

pytestmark = pytest.mark.unit


def test_new_history_is_empty(history):
    assert len(history) == 0
    assert history.all() == []


def test_add_stores_entry_with_injected_time(history, fixed_time):
    entry = history.add("add", {"a": 1, "b": 2}, 3)

    assert entry.operation == "add"
    assert entry.inputs == {"a": 1, "b": 2}
    assert entry.result == 3
    assert entry.timestamp == fixed_time
    assert len(history) == 1


def test_last_returns_most_recent_entry(history):
    history.add("add", {"a": 1, "b": 2}, 3)
    history.add("multiply", {"a": 2, "b": 5}, 10)

    assert history.last().operation == "multiply"


def test_last_on_empty_history_raises(history):
    with pytest.raises(LookupError, match="empty"):
        history.last()


def test_find_filters_by_operation(history):
    history.add("add", {}, 1)
    history.add("order", {}, 2)
    history.add("add", {}, 3)

    assert [e.result for e in history.find("add")] == [1, 3]
    assert history.find("unknown") == []


def test_max_size_drops_oldest_entries(fixed_time):
    small = CalculationHistory(max_size=2, clock=lambda: fixed_time)

    for i in range(4):
        small.add("op", {}, i)

    assert [e.result for e in small.all()] == [2, 3]


def test_clear_removes_everything(history):
    history.add("op", {}, 1)

    history.clear()

    assert len(history) == 0


def test_all_returns_a_copy(history):
    history.add("op", {}, 1)

    history.all().clear()

    assert len(history) == 1


def test_entry_keeps_its_own_copy_of_inputs(history):
    inputs = {"a": 1}
    entry = history.add("op", inputs, 1)

    inputs["a"] = 999

    assert entry.inputs == {"a": 1}


def test_default_clock_uses_real_time():
    entry = CalculationHistory().add("op", {}, 1)

    assert isinstance(entry.timestamp, datetime)


@pytest.mark.validation
@pytest.mark.parametrize("name", ["", "   "])
def test_add_rejects_empty_operation_name(history, name):
    with pytest.raises(ValueError, match="cannot be empty"):
        history.add(name, {}, 1)


@pytest.mark.validation
@pytest.mark.parametrize("size", [0, -1, 1.5, "10", True])
def test_invalid_max_size(size):
    with pytest.raises(ValueError, match="max_size"):
        CalculationHistory(max_size=size)
