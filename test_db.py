from db.database import (
    fetch_all,
    fetch_one,
    initialize_database,
)


def main():
    print("Initializing EKIP database...")

    initialize_database()

    print("Database schema initialized successfully.")

    tables = fetch_all(
        """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
          AND table_name IN (
              'users',
              'subjects',
              'documents',
              'submissions'
          )
        ORDER BY table_name;
        """
    )

    print("\nEKIP tables:")

    for table in tables:
        print(f"- {table['table_name']}")

    count = fetch_one(
        """
        SELECT
            (SELECT COUNT(*) FROM users) AS users,
            (SELECT COUNT(*) FROM subjects) AS subjects,
            (SELECT COUNT(*) FROM documents) AS documents,
            (SELECT COUNT(*) FROM submissions) AS submissions;
        """
    )

    print("\nRecord counts:")
    print(f"Users:       {count['users']}")
    print(f"Subjects:    {count['subjects']}")
    print(f"Documents:   {count['documents']}")
    print(f"Submissions: {count['submissions']}")

    print("\nPhase 1 database test passed.")


if __name__ == "__main__":
    main()