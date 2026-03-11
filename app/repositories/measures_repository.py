from app.repositories.base_repository import BaseRepository


class MeasuresRepository(BaseRepository):
    def insert_one(self, measure_code, measure_text):
        self.execute(
            """
        INSERT INTO measures (measure_code, measure_text)
        VALUES (%s, %s)
        ON CONFLICT (measure_code) DO NOTHING
        """,
            (measure_code, measure_text),
        )

    def get_all(self):
        return self.fetch_all("SELECT * FROM measures ORDER BY measure_code;")

    def get_by_code(self, measure_code):
        return self.fetch_one("SELECT * FROM measures WHERE measure_code = %s;", (measure_code,))
