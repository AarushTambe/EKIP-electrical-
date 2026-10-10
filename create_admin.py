import getpass

from db.database import initialize_database
from auth import create_user


def main():
    print("=" * 50)
    print("EKIP - Admin Account Provisioning")
    print("=" * 50)

    initialize_database()

    print("\nThis tool is for controlled administrator setup.")
    print("Do NOT expose this script as part of the student application.\n")

    name = input("Admin full name: ").strip()
    email = input("Admin email: ").strip()
    username = input("Admin username: ").strip()

    password = getpass.getpass("Admin password: ")
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
            role="admin",
        )

        print("\nAdmin account created successfully.")
        print(f"Name:     {user['name']}")
        print(f"Username: {user['username']}")
        print(f"Role:     {user['role']}")

    except Exception as e:
        print(f"\nError creating admin account: {e}")


if __name__ == "__main__":
    main()