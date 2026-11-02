import pytest

from database import (
    execute_query,
    execute_scalar,
    get_table_columns,
    get_users,
    get_orders,
)


def test_database_connection():
    result = execute_scalar("SELECT 1")

    assert result == 1


@pytest.mark.parametrize("table_name", ["users", "orders"])
def test_required_tables_exist(table_name):
    result = execute_scalar(
        """
        SELECT COUNT(*)
        FROM sqlite_master
        WHERE type = 'table'
        AND name = ?
        """,
        (table_name,),
    )

    assert result == 1


def test_users_count():
    assert execute_scalar(
        "SELECT COUNT(*) FROM users"
    ) == 20


def test_orders_count():
    assert execute_scalar(
        "SELECT COUNT(*) FROM orders"
    ) == 30


def test_user_ids_are_unique():
    total = execute_scalar(
        "SELECT COUNT(id) FROM users"
    )

    unique = execute_scalar(
        "SELECT COUNT(DISTINCT id) FROM users"
    )

    assert total == unique


def test_emails_are_unique():
    total = execute_scalar(
        "SELECT COUNT(email) FROM users"
    )

    unique = execute_scalar(
        "SELECT COUNT(DISTINCT email) FROM users"
    )

    assert total == unique


def test_all_users_have_required_data():
    invalid_rows = execute_query(
        """
        SELECT id
        FROM users
        WHERE name IS NULL
           OR email IS NULL
           OR age IS NULL
           OR status IS NULL
        """
    )

    assert invalid_rows == []


def test_all_orders_have_required_data():
    invalid_rows = execute_query(
        """
        SELECT id
        FROM orders
        WHERE user_id IS NULL
           OR product IS NULL
           OR amount IS NULL
           OR status IS NULL
        """
    )

    assert invalid_rows == []


def test_orders_reference_existing_users():
    invalid_rows = execute_query(
        """
        SELECT orders.id
        FROM orders
        LEFT JOIN users
            ON orders.user_id = users.id
        WHERE users.id IS NULL
        """
    )

    assert invalid_rows == []


def test_users_table_structure():
    columns = get_table_columns("users")

    column_names = [
        column[1]
        for column in columns
    ]

    assert column_names == [
        "id",
        "name",
        "email",
        "age",
        "status",
    ]


def test_orders_table_structure():
    columns = get_table_columns("orders")

    column_names = [
        column[1]
        for column in columns
    ]

    assert column_names == [
        "id",
        "user_id",
        "product",
        "amount",
        "status",
    ]


def test_get_users_returns_data():
    users = get_users()

    assert len(users) == 20
    assert users[0][0] == 1


def test_get_orders_returns_data():
    orders = get_orders()

    assert len(orders) == 30
    assert orders[0][0] == 1