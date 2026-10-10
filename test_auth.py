from db.database import initialize_database, execute_query
from auth import (
    hash_password,
    verify_password,
    create_user,
    authenticate_user,
)


def test_password_hashing():
    password = "TestPassword123!"

    hashed = hash_password(password)

    assert hashed != password
    assert hashed.startswith("pbkdf2_sha256$")

    assert verify_password(password, hashed)
    assert not verify_password("WrongPassword", hashed)

    print("✓ Password hashing test passed")


def test_user_authentication():
    username = "phase2_test_user"

    # Remove any previous test user.
    execute_query(
        "DELETE FROM users WHERE username = %s;",
        (username,),
    )

    create_user(
        name="Phase 2 Test User",
        email="phase2@test.local",
        username=username,
        password="TestPassword123!",
        role="student",
    )

    # Correct credentials
    user = authenticate_user(
        username,
        "TestPassword123!",
    )

    assert user is not None
    assert user["username"] == username
    assert user["role"] == "student"

    print("✓ Valid login test passed")

    # Wrong password
    user = authenticate_user(
        username,
        "WrongPassword123!",
    )

    assert user is None

    print("✓ Wrong password test passed")

    # Non-existent user
    user = authenticate_user(
        "does_not_exist",
        "TestPassword123!",
    )

    assert user is None

    print("✓ Non-existent user test passed")

    # Cleanup
    execute_query(
        "DELETE FROM users WHERE username = %s;",
        (username,),
    )

    print("✓ Test user cleaned up")


def main():
    print("Initializing EKIP database...")
    initialize_database()

    print("\nRunning Phase 2.1 authentication tests...\n")

    test_password_hashing()
    test_user_authentication()

    print("\nPhase 2.1 authentication foundation tests passed.")


if __name__ == "__main__":
    main()