from db.database import initialize_database, execute_query
from auth import create_user, authenticate_user


TEST_USERNAME = "phase2_admin_test"


def cleanup():
    execute_query(
        "DELETE FROM users WHERE username = %s;",
        (TEST_USERNAME,),
    )


def main():
    print("Initializing EKIP database...")
    initialize_database()

    print("\nRunning Phase 2.3 admin provisioning tests...\n")

    cleanup()

    # Create admin through the controlled provisioning function.
    user = create_user(
        name="Phase 2 Admin",
        email="phase2_admin@test.local",
        username=TEST_USERNAME,
        password="AdminPassword123!",
        role="admin",
    )

    assert user is not None
    assert user["username"] == TEST_USERNAME
    assert user["role"] == "admin"

    print("✓ Admin account created with admin role")

    # Verify admin authentication.
    authenticated = authenticate_user(
        TEST_USERNAME,
        "AdminPassword123!",
    )

    assert authenticated is not None
    assert authenticated["username"] == TEST_USERNAME
    assert authenticated["role"] == "admin"

    print("✓ Admin authentication works")

    # Verify incorrect password is rejected.
    failed_login = authenticate_user(
        TEST_USERNAME,
        "WrongPassword123!",
    )

    assert failed_login is None

    print("✓ Incorrect admin password rejected")

    cleanup()

    print("✓ Test admin cleaned up")

    print("\nPhase 2.3 admin provisioning tests passed.")


if __name__ == "__main__":
    main()