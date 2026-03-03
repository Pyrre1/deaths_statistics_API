class SexesRepository:
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def insert_one(self, sex_code, sex_text):
        with self.db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO sexes (sex_code, sex_text) 
                VALUES (%s, %s) 
                ON CONFLICT (sex_code) DO NOTHING
                """,
                (sex_code, sex_text)
            )
            self.db_connection.commit()

    def get_all(self):
        with self.db_connection.cursor() as cursor:
            cursor.execute("SELECT * FROM sexes ORDER BY sex_code;")
            return cursor.fetchall()