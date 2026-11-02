from pathlib import Path
import sqlite3


DATABASE_PATH = Path(__file__).with_name("test_database.db")


def get_connection():
    """Create a connection to the SQLite test database."""
    return sqlite3.connect(DATABASE_PATH)


def execute_query(query, params=()):
    """Execute a SELECT query and return all rows."""
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()


def execute_scalar(query, params=()):
    """Execute a query and return a single value."""
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(query, params)
        result = cursor.fetchone()

        return result[0] if result else None


def get_table_columns(table_name):
    """Return column information for a table."""
    return execute_query(f"PRAGMA table_info({table_name})")


def get_users():
    """Return all users."""
    return execute_query(
        """
        SELECT id, name, email, age, status
        FROM users
        ORDER BY id
        """
    )


def get_orders():
    """Return all orders."""
    return execute_query(
        """
        SELECT id, user_id, product, amount, status
        FROM orders
        ORDER BY id
        """
    )


if __name__ == "__main__":
    print("Database:", DATABASE_PATH)
    print("Users:", execute_scalar("SELECT COUNT(*) FROM users"))
    print("Orders:", execute_scalar("SELECT COUNT(*) FROM orders"))