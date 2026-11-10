# ============================================================
# app/db.py
# ATLAS-Enterprice-AI
# PostgreSQL connection management and database helpers
# ============================================================

from typing import Any, Mapping, Sequence

from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from app.config import settings


# ------------------------------------------------------------
# 1. GLOBAL CONNECTION POOL
# ------------------------------------------------------------

# Initially, no database connection pool exists.
# We create it when the application starts.

_pool: ConnectionPool | None = None


# ------------------------------------------------------------
# 2. INITIALIZE DATABASE CONNECTION POOL
# ------------------------------------------------------------

def init_db() -> None:
    """
    Create and open the PostgreSQL connection pool.

    The pool reuses database connections instead of creating
    a new connection for every query.
    """

    global _pool

    # Avoid creating multiple connection pools.
    if _pool is not None:
        return

    config = settings()

    # Check whether DATABASE_URL is configured.
    if not config.database_url:
        raise RuntimeError(
            "DATABASE_URL is missing. Configure it in your .env file."
        )

    # Create the connection pool.
    _pool = ConnectionPool(
        conninfo=config.database_url,
        min_size=1,
        max_size=10,
        timeout=30,
        open=False,
        kwargs={
            "row_factory": dict_row
        }
    )

    # Open the pool and wait for the initial connection.
    _pool.open(wait=True)


# ------------------------------------------------------------
# 3. GET DATABASE CONNECTION POOL
# ------------------------------------------------------------

def get_pool() -> ConnectionPool:
    """
    Return the initialized connection pool.

    Raises an error if the pool has not been initialized.
    """

    if _pool is None:
        raise RuntimeError(
            "Database is not initialized. Call init_db() first."
        )

    return _pool


# ------------------------------------------------------------
# 4. CLOSE DATABASE CONNECTION POOL
# ------------------------------------------------------------

def close_db() -> None:
    """
    Close all connections and release database resources.
    """

    global _pool

    if _pool is not None:
        _pool.close()
        _pool = None


# ------------------------------------------------------------
# 5. EXECUTE INSERT, UPDATE OR DELETE QUERIES
# ------------------------------------------------------------

def execute_query(
    query: str,
    params: Sequence[Any] | Mapping[str, Any] | None = None
) -> int:
    """
    Execute INSERT, UPDATE or DELETE queries.

    Returns the number of affected rows.
    """

    pool = get_pool()

    with pool.connection() as conn:

        result = conn.execute(
            query,
            params if params is not None else ()
        )

        return result.rowcount


# ------------------------------------------------------------
# 6. FETCH A SINGLE DATABASE RECORD
# ------------------------------------------------------------

def fetch_one(
    query: str,
    params: Sequence[Any] | Mapping[str, Any] | None = None
) -> dict[str, Any] | None:
    """
    Execute a SELECT query and return one record.

    Returns None if no matching record exists.
    """

    pool = get_pool()

    with pool.connection() as conn:

        result = conn.execute(
            query,
            params if params is not None else ()
        )

        return result.fetchone()


# ------------------------------------------------------------
# 7. FETCH MULTIPLE DATABASE RECORDS
# ------------------------------------------------------------

def fetch_all(
    query: str,
    params: Sequence[Any] | Mapping[str, Any] | None = None
) -> list[dict[str, Any]]:
    """
    Execute a SELECT query and return all matching records.
    """

    pool = get_pool()

    with pool.connection() as conn:

        result = conn.execute(
            query,
            params if params is not None else ()
        )

        return result.fetchall()


# ------------------------------------------------------------
# 8. DATABASE HEALTH CHECK
# ------------------------------------------------------------

def check_db_connection() -> bool:
    """
    Check whether PostgreSQL is reachable.

    Returns True if the database responds successfully.
    """

    try:
        result = fetch_one("SELECT 1 AS database_status")

        return result is not None and result["database_status"] == 1

    except Exception:
        return False