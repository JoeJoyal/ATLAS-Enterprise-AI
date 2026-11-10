
# ============================================================
# scripts/init_db.py
# Create and verify PostgreSQL database schema
# ============================================================

from pathlib import Path

import psycopg

from app.config import settings


# ------------------------------------------------------------
# 1. EXPECTED DATABASE TABLES
# ------------------------------------------------------------

# These are the six tables defined in infra/schema.sql.

EXPECTED_TABLES = {
    "documents",
    "chat_sessions",
    "chat_messages",
    "hitl_approvals",
    "feedback",
    "audit_events",
}


# ------------------------------------------------------------
# 2. LOCATE THE SQL SCHEMA FILE
# ------------------------------------------------------------

def get_schema_path() -> Path:
    """
    Locate infra/schema.sql relative to the project root.

    This works regardless of the directory from which
    the script is launched, provided the project is intact.
    """

    project_root = Path(__file__).resolve().parents[1]

    schema_path = project_root / "infra" / "schema.sql"

    if not schema_path.exists():
        raise FileNotFoundError(
            f"Database schema file not found: {schema_path}"
        )

    return schema_path


# ------------------------------------------------------------
# 3. VERIFY DATABASE TABLES
# ------------------------------------------------------------

def verify_tables(conn: psycopg.Connection) -> bool:
    """
    Check whether all expected database tables exist.

    Returns True when all six tables are available.
    """

    query = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
          AND table_type = 'BASE TABLE'
    """

    with conn.cursor() as cursor:

        cursor.execute(query)

        rows = cursor.fetchall()

    # Extract table names from the query result.
    existing_tables = {
        row[0] for row in rows
    }

    # Identify tables that are missing.
    missing_tables = EXPECTED_TABLES - existing_tables

    # Display existing expected tables.
    print("\nDatabase table verification:")

    for table in sorted(EXPECTED_TABLES):

        if table in existing_tables:
            print(f"  [OK] {table}")

        else:
            print(f"  [MISSING] {table}")

    if missing_tables:

        raise RuntimeError(
            f"Database schema verification failed. "
            f"Missing tables: {sorted(missing_tables)}"
        )

    return True


# ------------------------------------------------------------
# 4. VERIFY DATABASE INDEXES
# ------------------------------------------------------------

def verify_indexes(conn: psycopg.Connection) -> int:
    """
    Count indexes created in the public schema.
    """

    query = """
        SELECT COUNT(*) AS total_indexes
        FROM pg_indexes
        WHERE schemaname = 'public'
    """

    with conn.cursor() as cursor:

        cursor.execute(query)

        result = cursor.fetchone()

    total_indexes = result[0]

    print(f"\nTotal database indexes: {total_indexes}")

    return total_indexes


# ------------------------------------------------------------
# 5. INITIALIZE DATABASE
# ------------------------------------------------------------

def initialize_database() -> None:
    """
    Execute infra/schema.sql and verify the database schema.
    """

    print("=" * 55)
    print("ATLAS-Enterprice-AI Database Initialization")
    print("=" * 55)

    # Load environment configuration.
    config = settings()

    # Validate database connection URL.
    if not config.database_url:

        raise RuntimeError(
            "DATABASE_URL is missing. Check your .env file."
        )

    # Locate the SQL file.
    schema_path = get_schema_path()

    print(f"\nSchema file: {schema_path}")

    # Read the complete SQL schema.
    schema_sql = schema_path.read_text(encoding="utf-8")

    if not schema_sql.strip():

        raise RuntimeError(
            "The database schema file is empty."
        )

    print("\nConnecting to PostgreSQL...")

    # --------------------------------------------------------
    # Establish a direct database connection.
    # --------------------------------------------------------

    with psycopg.connect(
        conninfo=config.database_url,
        connect_timeout=30
    ) as conn:

        print("[OK] PostgreSQL connected successfully.")

        # ----------------------------------------------------
        # Execute all SQL statements.
        # prepare=False allows the SQL script to contain
        # multiple statements in one execution.
        # ----------------------------------------------------

        print("\nExecuting database schema...")

        with conn.cursor() as cursor:

            cursor.execute(
                schema_sql,
                prepare=False
            )

        print("[OK] Schema execution completed.")

        # ----------------------------------------------------
        # Verify all expected tables.
        # ----------------------------------------------------

        verify_tables(conn)

        # ----------------------------------------------------
        # Verify database indexes.
        # ----------------------------------------------------

        verify_indexes(conn)

    # Connection closes automatically after the context exits.
    print("\n[OK] PostgreSQL connection closed.")

    print("\n" + "=" * 55)
    print("DATABASE INITIALIZATION SUCCESSFUL!")
    print("=" * 55)


# ------------------------------------------------------------
# 6. SCRIPT ENTRY POINT
# ------------------------------------------------------------

if __name__ == "__main__":

    initialize_database()
