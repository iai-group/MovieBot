"""Database manager for providing database context."""

import sqlite3


class DatabaseManager:
    def __init__(self, db_name: str) -> None:
        """Database manager for providing database context.

        Args:
            db_name: Path to the database file.
        """
        self.db_name = db_name

    def __enter__(self) -> sqlite3.Cursor:
        """Returns a cursor to the database."""
        self.conn = sqlite3.connect(self.db_name)
        return self.conn.cursor()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Closes the database connection."""
        self.conn.close()
