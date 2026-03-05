from app.repositories.base_repository import BaseRepository

class SexesRepository(BaseRepository):
    def insert_one(self, sex_code, sex_text):
        self.execute(
          """
          INSERT INTO sexes (sex_code, sex_text) 
          VALUES (%s, %s) 
          ON CONFLICT (sex_code) DO NOTHING
          """,
          (sex_code, sex_text)
        )
        self.db_connection.commit()

    def get_all(self):
      return self.fetch_all("SELECT * FROM sexes ORDER BY sex_code;")