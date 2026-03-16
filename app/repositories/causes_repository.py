from app.repositories.base_repository import BaseRepository


class CausesRepository(BaseRepository):
    def insert_one(self, diagnosis_code, diagnosis_text):
        self.execute(
            """
        INSERT INTO causes (diagnosis_code, diagnosis_text)
        VALUES (%s, %s)
        ON CONFLICT (diagnosis_code) DO NOTHING
        """,
            (diagnosis_code, diagnosis_text),
        )

    def get_all(self, limit=100, offset=0):
        return self.fetch_all(
            "SELECT * FROM causes ORDER BY diagnosis_code LIMIT %s OFFSET %s;",
            (limit, offset)
        )

    def count_all(self):
        result = self.fetch_one("SELECT COUNT(*) AS total FROM causes;")
        return result["total"] if result else 0

    def get_by_code(self, diagnosis_code):
        return self.fetch_one(
            "SELECT * FROM causes WHERE diagnosis_code = %s;",
            (diagnosis_code,),
        )
