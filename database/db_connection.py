"""
Database Connection Manager for PurrfectMatch.
Implements the Singleton Pattern with Dual-Mode connectivity (Option A):
1. Primary: XAMPP MySQL (purrfect_match_db on 127.0.0.1:3306)
2. Fallback: Offline SQLite (purrfect_match.db)

Seamlessly detects and uses XAMPP MySQL when running, and falls back to
local SQLite without crashing when offline.
"""

import os
import sqlite3

try:
    import mysql.connector
    from mysql.connector import Error as MySQLError
    MYSQL_AVAILABLE = True
except ImportError:
    mysql = None
    MySQLError = Exception
    MYSQL_AVAILABLE = False


class DatabaseConnection:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(
        self,
        mysql_host="127.0.0.1",
        mysql_port=3306,
        mysql_user="root",
        mysql_password="",
        mysql_database="purrfect_match_db",
        sqlite_filename="purrfect_match.db",
    ):
        if self._initialized:
            return

        self.mysql_config = {
            "host": mysql_host,
            "port": mysql_port,
            "user": mysql_user,
            "password": mysql_password,
            "database": mysql_database,
            "connection_timeout": 3,
        }

        db_dir = os.path.dirname(__file__)
        self.sqlite_path = os.path.join(db_dir, sqlite_filename)
        self.db_path = self.sqlite_path  # Backwards compatibility

        self.connection = None
        self.db_type = None  # "mysql" or "sqlite"
        self._initialized = True

    def _try_mysql_connection(self):
        """Attempts to connect to MySQL (XAMPP). Returns connection or None."""
        if not MYSQL_AVAILABLE:
            return None

        try:
            # 1. Connect to MySQL server to ensure database exists
            server_conn = mysql.connector.connect(
                host=self.mysql_config["host"],
                port=self.mysql_config["port"],
                user=self.mysql_config["user"],
                password=self.mysql_config["password"],
                connection_timeout=self.mysql_config["connection_timeout"]
            )
            cursor = server_conn.cursor()
            db_name = self.mysql_config["database"]
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{db_name}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
            )
            cursor.close()
            server_conn.close()

            # 2. Connect directly to target database
            conn = mysql.connector.connect(**self.mysql_config)
            return conn
        except Exception:
            # Connection failed (e.g. XAMPP MySQL is not started)
            return None

    def connect(self):
        """Establishes or returns the active database connection."""
        # Check existing connection
        if self.connection is not None:
            if self.db_type == "mysql":
                try:
                    if hasattr(self.connection, "is_connected") and self.connection.is_connected():
                        return self.connection
                except Exception:
                    pass
                
                # Attempt to reconnect to MySQL
                conn = self._try_mysql_connection()
                if conn is not None:
                    self.connection = conn
                    return self.connection
                else:
                    # Switch to SQLite if MySQL went offline
                    print("[Database Notice]: XAMPP MySQL connection lost. Falling back to SQLite.")
                    self.db_type = "sqlite"
                    self.connection = None
            else:
                return self.connection

        # Attempt MySQL (XAMPP) first
        mysql_conn = self._try_mysql_connection()
        if mysql_conn is not None:
            self.connection = mysql_conn
            self.db_type = "mysql"
            return self.connection

        # Fallback to SQLite (Offline mode)
        self.db_type = "sqlite"
        self.connection = sqlite3.connect(self.sqlite_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON;")
        return self.connection

    def initialize_database(self):
        """
        Initializes schema and seed data for the active database engine (MySQL or SQLite).
        """
        conn = self.connect()

        if self.db_type == "mysql":
            try:
                cursor = conn.cursor()
                cursor.execute("SHOW TABLES LIKE 'cats';")
                cat_table = cursor.fetchone()
                cursor.close()

                if not cat_table:
                    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
                    if os.path.exists(schema_path):
                        with open(schema_path, "r", encoding="utf-8") as f:
                            sql_content = f.read()

                        cursor = conn.cursor()
                        # Execute individual DDL and DML statements
                        for raw_stmt in sql_content.split(";"):
                            stmt = raw_stmt.strip()
                            # Skip comments or empty statements
                            if stmt and not stmt.startswith("--") and not stmt.startswith("/*"):
                                cursor.execute(stmt)
                        conn.commit()
                        cursor.close()

                msg = (
                    f"Connected to XAMPP MySQL "
                    f"({self.mysql_config['database']} on {self.mysql_config['host']}:{self.mysql_config['port']})"
                )
                print(f"[Database]: {msg}")
                return True, msg
            except Exception as e:
                print(f"[Database Warning]: MySQL initialization error ({e}). Falling back to SQLite.")
                self.close()
                self.db_type = "sqlite"
                return self._init_sqlite()
        else:
            return self._init_sqlite()

    def _init_sqlite(self):
        """Initializes SQLite schema."""
        try:
            conn = self.connect()
            schema_path = os.path.join(os.path.dirname(__file__), "schema_sqlite.sql")
            if os.path.exists(schema_path):
                with open(schema_path, "r", encoding="utf-8") as f:
                    sql_script = f.read()
                conn.executescript(sql_script)
                conn.commit()
            msg = f"Connected to offline SQLite ({os.path.basename(self.sqlite_path)})"
            print(f"[Database]: {msg}")
            return True, msg
        except sqlite3.Error as e:
            return False, f"SQLite Initialization Error: {e}"

    def _prepare_query(self, query: str) -> str:
        """Translates MySQL %s parameter syntax to SQLite ? syntax when running on SQLite."""
        if self.db_type == "sqlite":
            return query.replace("%s", "?")
        return query

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
        if self.db_type == "mysql":
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute(query, params or ())
                return cursor.fetchall()
            finally:
                cursor.close()
        else:
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
        if self.db_type == "mysql":
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute(query, params or ())
                return cursor.fetchone()
            finally:
                cursor.close()
        else:
            cursor = conn.cursor()
            try:
                prepared_query = self._prepare_query(query)
                cursor.execute(prepared_query, params or ())
                row = cursor.fetchone()
                return dict(row) if row else None
            finally:
                cursor.close()

    def get_db_type(self) -> str:
        """Returns the human-readable database type currently in use."""
        if self.db_type is None:
            self.connect()
        return "MySQL (XAMPP)" if self.db_type == "mysql" else "SQLite (Offline)"

    @property
    def is_mysql(self) -> bool:
        if self.db_type is None:
            self.connect()
        return self.db_type == "mysql"

    @property
    def is_sqlite(self) -> bool:
        if self.db_type is None:
            self.connect()
        return self.db_type == "sqlite"

    def close(self):
        """Closes the connection if open."""
        if self.connection:
            try:
                self.connection.close()
            except Exception:
                pass
            self.connection = None
