class BaseRepository:
    def __init__(self, db_connection):
      self.db_connection = db_connection

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
