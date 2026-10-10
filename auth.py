import hashlib
import hmac
import secrets

from db.database import fetch_one, execute_query


ITERATIONS = 310_000
SALT_BYTES = 16


def hash_password(password: str) -> str:
    """Hash a password using PBKDF2-HMAC-SHA256."""

    if not password:
        raise ValueError("Password cannot be empty.")

    salt = secrets.token_bytes(SALT_BYTES)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        ITERATIONS,
    )

    return (
        f"pbkdf2_sha256$"
        f"{ITERATIONS}$"
        f"{salt.hex()}$"
        f"{password_hash.hex()}"
    )


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify a password against a stored PBKDF2 hash."""

    if not password or not stored_hash:
        return False

    try:
        algorithm, iterations, salt_hex, hash_hex = stored_hash.split("$")

        if algorithm != "pbkdf2_sha256":
            return False

        iterations = int(iterations)
        salt = bytes.fromhex(salt_hex)
        expected_hash = bytes.fromhex(hash_hex)

        actual_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            iterations,
        )

        return hmac.compare_digest(actual_hash, expected_hash)

    except (ValueError, TypeError):
        return False


def create_user(
    name: str,
    email: str,
    username: str,
    password: str,
    role: str = "student",
):
    """Create a user in PostgreSQL."""

    if role not in ("student", "admin"):
        raise ValueError("Role must be 'student' or 'admin'.")

    if not name.strip():
        raise ValueError("Name cannot be empty.")

    if not email.strip():
        raise ValueError("Email cannot be empty.")

    if not username.strip():
        raise ValueError("Username cannot be empty.")

    if not password:
        raise ValueError("Password cannot be empty.")

    password_hash = hash_password(password)

    query = """
        INSERT INTO users
            (name, email, username, password_hash, role)
        VALUES
            (%s, %s, %s, %s, %s)
        RETURNING id, name, email, username, role, created_at;
    """

    # Your database.py execute_query() already handles the database
    # operation according to its own existing interface.
    execute_query(
        query,
        (
            name.strip(),
            email.strip(),
            username.strip(),
            password_hash,
            role,
        ),
    )

    return fetch_one(
        """
        SELECT
            id,
            name,
            email,
            username,
            role,
            created_at
        FROM users
        WHERE username = %s;
        """,
        (username.strip(),),
    )


def authenticate_user(username: str, password: str):
    """Authenticate a user using username and password."""

    if not username or not password:
        return None

    query = """
        SELECT
            id,
            name,
            email,
            username,
            password_hash,
            role,
            created_at
        FROM users
        WHERE username = %s;
    """

    user = fetch_one(query, (username.strip(),))

    if not user:
        return None

    if not verify_password(password, user["password_hash"]):
        return None

    return {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "username": user["username"],
        "role": user["role"],
        "created_at": user["created_at"],
    }


def is_admin(user) -> bool:
    """Return True if the user has the admin role."""
    return bool(user and user.get("role") == "admin")


def is_student(user) -> bool:
    """Return True if the user has the student role."""
    return bool(user and user.get("role") == "student")