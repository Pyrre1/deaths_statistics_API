class BaseRepository:
    AGGREGATE_CODES = {"age_code": 99, "sex_code": 3, "region_code": 0, "diagnosis_code": "99"}

    def __init__(self, db_connection):
        """Store the database connection for use by all repository methods."""
        self.db_connection = db_connection

    def _build_non_aggregate_filter(self):
        """Returns a SQL WHERE clause to exclude affregate rows"""
        return """
        age_code != 99
        AND sex_code != 3
        AND diagnosis_code != '99'
        AND measure_code = 1
        """

    def execute(self, query, params=None):
        """Execute a write query (INSERT, UPDATE, DELETE) without returning rows."""
        with self.db_connection.cursor() as cursor:
            cursor.execute(query, params)
            self.db_connection.commit()

    def fetch_all(self, query, params=None):
        """Execute a SELECT query and return all matching rows as dicts."""
        with self.db_connection.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()

    def fetch_one(self, query, params=None):
        """Execute a SELECT query and return a single row as a dict."""
        with self.db_connection.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchone()

    def fetch_one_write(self, query, params=None):
        """Execute a write query and return the affected row (e.g. for RETURNING clauses)."""
        with self.db_connection.cursor() as cursor:
            cursor.execute(query, params)
            self.db_connection.commit()
            return cursor.fetchone()
