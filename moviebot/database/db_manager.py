import sqlite3


class DatabaseManager:
    def __init__(self, db_name):
        """Database manager for providing database context.

        Args:
            db_name: path to the database file.
        """
        self.db_name = db_name

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_name)
        return self.conn.cursor()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()
