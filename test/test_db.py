from app.db import (
    init_db,
    close_db,
    check_db_connection,
    fetch_one
)

try:

    # Step 1: Initialize the connection pool
    print("Initializing PostgreSQL connection...")

    init_db()

    # Step 2: Check database connectivity
    if check_db_connection():

        print("PostgreSQL connected successfully!")

    else:

        print("PostgreSQL connection failed!")

    # Step 3: Check whether our schema tables exist
    query = """
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'public'
    ORDER BY table_name
    """

    result = fetch_one(
        "SELECT COUNT(*) AS total_tables "
        "FROM information_schema.tables "
        "WHERE table_schema = 'public'"
    )

    print("Total database tables:", result["total_tables"])

finally:

    # Step 4: Close database connections
    close_db()

    print("Database connection pool closed.")