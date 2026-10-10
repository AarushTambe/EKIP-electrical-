import getpass

from db.database import initialize_database
from auth import create_user


def main():
    print("=" * 50)
    print("EKIP - Student Account Creation")
    print("=" * 50)

    initialize_database()

    print("\nCreate a new student account.\n")

    name = input("Full name: ").strip()
    email = input("Email: ").strip()
    username = input("Username: ").strip()

    password = getpass.getpass("Password: ")
    confirm_password = getpass.getpass("Confirm password: ")

    if not name or not email or not username:
        print("\nError: Name, email, and username are required.")
        return

    if not password:
        print("\nError: Password cannot be empty.")
        return

    if password != confirm_password:
        print("\nError: Passwords do not match.")
        return

    try:
        user = create_user(
            name=name,
            email=email,
            username=username,
            password=password,
            role="student",
        )

        print("\nStudent account created successfully.")
        print(f"Name:     {user['name']}")
        print(f"Username: {user['username']}")
        print(f"Role:     {user['role']}")

    except Exception as e:
        print(f"\nError creating student account: {e}")


if __name__ == "__main__":
    main()