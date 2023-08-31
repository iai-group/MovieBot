"""Class for managing the users database."""

import sqlite3
from typing import Optional

from werkzeug.security import check_password_hash, generate_password_hash

from moviebot.database.db_manager import DatabaseManager


class UserDB:
    def __init__(self, users_db_path: str = "data/users.db") -> None:
        """Class for managing the users database.

        Args:
            users_db_path: Path to users database.
        """
        self.manager = DatabaseManager(users_db_path)

    def get_user_id(self, username: str) -> Optional[int]:
        """Gets user ID from username.

        Args:
            username: Username of user.

        Returns:
            User ID.
        """
        with self.manager as cursor:
            cursor.execute("SELECT id FROM users WHERE username=?", (username,))
            user_id = cursor.fetchone()

        return user_id[0] if user_id else None

    def register_user(self, username: str, password: str) -> bool:
        """Registers user.

        Args:
            username: Username of user.
            password: Password of user.

        Returns:
            Whether user was registered successfully.
        """
        hashed_password = generate_password_hash(password, method="scrypt")

        with self.manager as cursor:
            try:
                cursor.execute(
                    "INSERT INTO users (username, password) VALUES (?, ?)",
                    (username, hashed_password),
                )
                cursor.connection.commit()
                return True
            except sqlite3.IntegrityError:
                return False

    def verify_user(self, username: str, password: str) -> bool:
        """Verifies user.

        Args:
            username: Username of user.
            password: Password of user.

        Returns:
            Whether user was verified successfully.
        """
        with self.manager as cursor:
            cursor.execute(
                "SELECT password FROM users WHERE username=?", (username,)
            )
            stored_password = cursor.fetchone()

        if stored_password and check_password_hash(
            stored_password[0], password
        ):
            return True
        else:
            return False

    def setup_db(self) -> None:
        """Sets up users database."""
        with self.manager as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL
                )
            """
            )
            cursor.connection.commit()
