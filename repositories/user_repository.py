from database.db import get_connection


class UserRepository:

    def find_by_username(self, username: str) -> dict | None:
        """Return user row as dict, or None if not found."""
        conn = get_connection()
        row = conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()
        conn.close()
        return dict(row) if row else None

    def find_by_credentials(self, username: str, hashed_password: str) -> dict | None:
        """Return user row if username + password match, else None."""
        conn = get_connection()
        row = conn.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (username, hashed_password)
        ).fetchone()
        conn.close()
        return dict(row) if row else None

    def create(self, username: str, firstname: str, lastname: str, hashed_password: str) -> bool:
        """Insert a new user. Returns False if username is already taken."""
        import sqlite3
        try:
            conn = get_connection()
            conn.execute(
                "INSERT INTO users (username, firstname, lastname, password) VALUES (?, ?, ?, ?)",
                (username, firstname, lastname, hashed_password)
            )
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False


# Singleton instance used by the service layer
user_repository = UserRepository()