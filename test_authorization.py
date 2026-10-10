from db.database import initialize_database, execute_query
from auth import create_user, authenticate_user, is_admin, is_student


STUDENT_USERNAME = "phase2_auth_student"
ADMIN_USERNAME = "phase2_auth_admin"


def cleanup():
    execute_query(
        "DELETE FROM users WHERE username IN (%s, %s);",
        (STUDENT_USERNAME, ADMIN_USERNAME),
    )


def main():
    print("Initializing EKIP database...")
    initialize_database()

    print("\nRunning Phase 2.7 authorization tests...\n")

    cleanup()

    # --------------------------------------------------------
    # Create test student
    # --------------------------------------------------------

    create_user(
        name="Authorization Student",
        email="auth_student@test.local",
        username=STUDENT_USERNAME,
        password="StudentPassword123!",
        role="student",
    )

    print("✓ Test student created")

    # --------------------------------------------------------
    # Create test admin
    # --------------------------------------------------------

    create_user(
        name="Authorization Admin",
        email="auth_admin@test.local",
        username=ADMIN_USERNAME,
        password="AdminPassword123!",
        role="admin",
    )

    print("✓ Test admin created")

    # --------------------------------------------------------
    # Authenticate student
    # --------------------------------------------------------

    student = authenticate_user(
        STUDENT_USERNAME,
        "StudentPassword123!",
    )

    assert student is not None
    assert student["role"] == "student"
    assert is_student(student)
    assert not is_admin(student)

    print("✓ Student receives student role")
    print("✓ Student is recognized as student")
    print("✓ Student is not recognized as admin")

    # --------------------------------------------------------
    # Authenticate admin
    # --------------------------------------------------------

    admin = authenticate_user(
        ADMIN_USERNAME,
        "AdminPassword123!",
    )

    assert admin is not None
    assert admin["role"] == "admin"
    assert is_admin(admin)
    assert not is_student(admin)

    print("✓ Admin receives admin role")
    print("✓ Admin is recognized as admin")
    print("✓ Admin is not recognized as student")

    # --------------------------------------------------------
    # Verify incorrect passwords
    # --------------------------------------------------------

    assert (
        authenticate_user(
            STUDENT_USERNAME,
            "WrongPassword123!",
        )
        is None
    )

    assert (
        authenticate_user(
            ADMIN_USERNAME,
            "WrongPassword123!",
        )
        is None
    )

    print("✓ Incorrect passwords rejected for both roles")

    # --------------------------------------------------------
    # Cleanup
    # --------------------------------------------------------

    cleanup()

    print("✓ Authorization test users cleaned up")

    print("\nPhase 2.7 authorization tests passed.")


if __name__ == "__main__":
    main()