import re

import pytest

from database import (
    execute_query,
    get_users,
    get_orders,
)


VALID_USER_STATUSES = {
    "active",
    "inactive",
}

VALID_ORDER_STATUSES = {
    "completed",
    "pending",
    "cancelled",
}


@pytest.mark.parametrize(
    "status",
    sorted(VALID_USER_STATUSES),
)
def test_user_statuses_are_valid(status):
    result = execute_query(
        """
        SELECT COUNT(*)
        FROM users
        WHERE status = ?
        """,
        (status,),
    )

    assert result[0][0] > 0


def test_all_user_statuses_are_allowed():
    rows = execute_query(
        "SELECT DISTINCT status FROM users"
    )

    statuses = {
        row[0]
        for row in rows
    }

    assert statuses.issubset(
        VALID_USER_STATUSES
    )


def test_all_order_statuses_are_allowed():
    rows = execute_query(
        "SELECT DISTINCT status FROM orders"
    )

    statuses = {
        row[0]
        for row in rows
    }

    assert statuses.issubset(
        VALID_ORDER_STATUSES
    )


def test_user_ages_are_in_valid_range():
    invalid_rows = execute_query(
        """
        SELECT id, age
        FROM users
        WHERE age < 18
           OR age > 100
        """
    )

    assert invalid_rows == []


def test_order_amounts_are_positive():
    invalid_rows = execute_query(
        """
        SELECT id, amount
        FROM orders
        WHERE amount <= 0
        """
    )

    assert invalid_rows == []


def test_user_emails_have_valid_format():
    email_pattern = re.compile(
        r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    )

    users = get_users()

    invalid_emails = [
        email
        for _, _, email, _, _ in users
        if not email_pattern.match(email)
    ]

    assert invalid_emails == []


def test_user_names_are_not_empty():
    users = get_users()

    invalid_names = [
        name
        for _, name, _, _, _ in users
        if not name.strip()
    ]

    assert invalid_names == []


def test_order_products_are_not_empty():
    orders = get_orders()

    invalid_products = [
        product
        for _, _, product, _, _ in orders
        if not product.strip()
    ]

    assert invalid_products == []


@pytest.mark.parametrize(
    "query, expected_minimum",
    [
        (
            "SELECT COUNT(*) FROM users WHERE age >= 18",
            20,
        ),
        (
            "SELECT COUNT(*) FROM users WHERE status = 'active'",
            1,
        ),
        (
            "SELECT COUNT(*) FROM orders WHERE amount > 0",
            30,
        ),
        (
            "SELECT COUNT(*) FROM orders WHERE status = 'completed'",
            1,
        ),
    ],
)
def test_expected_data_exists(
    query,
    expected_minimum,
):
    result = execute_query(query)

    assert result[0][0] >= expected_minimum


def test_user_order_relationship():
    rows = execute_query(
        """
        SELECT users.id, COUNT(orders.id)
        FROM users
        LEFT JOIN orders
            ON users.id = orders.user_id
        GROUP BY users.id
        """
    )

    assert len(rows) == 20

    for user_id, order_count in rows:
        assert user_id > 0
        assert order_count >= 0


def test_completed_orders_have_positive_amount():
    invalid_rows = execute_query(
        """
        SELECT id, amount
        FROM orders
        WHERE status = 'completed'
        AND amount <= 0
        """
    )

    assert invalid_rows == []