from db.database import initialize_database, execute_query
from auth import create_user, authenticate_user


TEST_USERNAME = "phase2_student_test"


def cleanup():
    execute_query(
        "DELETE FROM users WHERE username = %s;",
        (TEST_USERNAME,),
    )


def main():
    print("Initializing EKIP database...")
    initialize_database()

    print("\nRunning Phase 2.2 student account tests...\n")

    cleanup()

    # Create student
    user = create_user(
        name="Phase 2 Student",
        email="phase2_student@test.local",
        username=TEST_USERNAME,
        password="StudentPassword123!",
        role="student",
    )

    assert user is not None
    assert user["username"] == TEST_USERNAME
    assert user["role"] == "student"

    print("✓ Student account created")

    # Authenticate student
    authenticated = authenticate_user(
        TEST_USERNAME,
        "StudentPassword123!",
    )

    assert authenticated is not None
    assert authenticated["username"] == TEST_USERNAME
    assert authenticated["role"] == "student"

    print("✓ Student authentication works")

    # Verify student is not admin
    assert authenticated["role"] != "admin"

    print("✓ Student does not have admin role")

    # Cleanup
    cleanup()

    print("✓ Test student cleaned up")

    print("\nPhase 2.2 student account tests passed.")


if __name__ == "__main__":
    main()