class BaseRepository:
    AGGREGATE_CODES = {"age_code": 99, "sex_code": 3, "region_code": 0, "diagnosis_code": "99"}

    def __init__(self, db_connection):
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
        with self.db_connection.cursor() as cursor:
            cursor.execute(query, params)
            self.db_connection.commit()

    def fetch_all(self, query, params=None):
        with self.db_connection.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()

    def fetch_one(self, query, params=None):
        with self.db_connection.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchone()

    def fetch_one_write(self, query, params=None):
        with self.db_connection.cursor() as cursor:
            cursor.execute(query, params)
            self.db_connection.commit()
            return cursor.fetchone()
