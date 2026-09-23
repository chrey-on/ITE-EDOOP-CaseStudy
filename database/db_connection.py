"""
Database Connection Manager for PurrfectMatch.
Implements the Singleton Pattern using Python's built-in SQLite3.
100% Offline, Zero-installation required. Automatically creates database and seed data.
"""

import os
import sqlite3


class DatabaseConnection:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, db_filename="purrfect_match.db"):
        if self._initialized:
            return

        db_dir = os.path.dirname(__file__)
        self.db_path = os.path.join(db_dir, db_filename)
        self.connection = None
        self._initialized = True

    def connect(self):
        """Establishes or returns the SQLite connection."""
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
            # Enable foreign key support in SQLite
            self.connection.execute("PRAGMA foreign_keys = ON;")
        return self.connection

    def initialize_database(self):
        """
        Initializes the SQLite database and runs schema_sqlite.sql
        to create tables and seed initial sample data.
        """
        try:
            conn = self.connect()
            schema_path = os.path.join(os.path.dirname(__file__), "schema_sqlite.sql")
            
            if os.path.exists(schema_path):
                with open(schema_path, "r", encoding="utf-8") as f:
                    sql_script = f.read()
                conn.executescript(sql_script)
                conn.commit()

            return True, "SQLite database initialized successfully."
        except sqlite3.Error as e:
            return False, f"SQLite Initialization Error: {e}"

    def _prepare_query(self, query: str) -> str:
        """Translates standard MySQL %s parameter syntax to SQLite ? syntax."""
        return query.replace("%s", "?")

    def execute_query(self, query, params=None):
        """
        Executes an INSERT, UPDATE, or DELETE query.
        Returns a dict containing lastrowid and rowcount.
        """
        conn = self.connect()
        cursor = conn.cursor()
        try:
            prepared_query = self._prepare_query(query)
            cursor.execute(prepared_query, params or ())
            conn.commit()
            return {"lastrowid": cursor.lastrowid, "rowcount": cursor.rowcount}
        finally:
            cursor.close()

    def fetch_all(self, query, params=None):
        """
        Executes a SELECT query and returns all matching rows as dictionaries.
        """
        conn = self.connect()
        cursor = conn.cursor()
        try:
            prepared_query = self._prepare_query(query)
            cursor.execute(prepared_query, params or ())
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            cursor.close()

    def fetch_one(self, query, params=None):
        """
        Executes a SELECT query and returns the first matching row as a dictionary.
        """
        conn = self.connect()
        cursor = conn.cursor()
        try:
            prepared_query = self._prepare_query(query)
            cursor.execute(prepared_query, params or ())
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            cursor.close()

    def close(self):
        """Closes the connection if open."""
        if self.connection:
            self.connection.close()
            self.connection = None
