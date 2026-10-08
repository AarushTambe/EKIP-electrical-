import os
from pathlib import Path

import psycopg
from psycopg.rows import dict_row


BASE_DIR = Path(__file__).resolve().parent.parent
SCHEMA_PATH = BASE_DIR / "db" / "schema.sql"


def get_database_url():
    """
    Read the PostgreSQL connection URL from the environment.

    Example:
    DATABASE_URL=postgresql://username:password@localhost:5432/ekip
    """

    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError(
            "DATABASE_URL is not configured. "
            "Set it in your environment before starting EKIP."
        )

    return database_url


def get_connection():
    """
    Create a PostgreSQL connection.
    """

    return psycopg.connect(
        get_database_url(),
        row_factory=dict_row,
    )


def initialize_database():
    """
    Create the EKIP application tables if they do not already exist.
    """

    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(
            f"Database schema not found: {SCHEMA_PATH}"
        )

    schema = SCHEMA_PATH.read_text(encoding="utf-8")

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(schema)

        connection.commit()


def execute_query(query, params=None):
    """
    Execute a query that does not return rows.
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, params)

        connection.commit()


def fetch_one(query, params=None):
    """
    Execute a query and return one row.
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchone()


def fetch_all(query, params=None):
    """
    Execute a query and return all rows.
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()