from app.repositories.base_repository import BaseRepository

class AgesRepository(BaseRepository):
    def insert_one(self, age_code, age_text):
      self.execute(
        """
        INSERT INTO ages (age_code, age_text) 
        VALUES (%s, %s) 
        ON CONFLICT (age_code) DO NOTHING
        """,
        (age_code, age_text)
      )
    def get_all(self):
      return self.fetch_all(
          "SELECT * FROM ages ORDER BY age_code;"
      )

    def get_by_code(self, age_code):
      return self.fetch_one(
          "SELECT * FROM ages WHERE age_code = %s;",
          (age_code,)
      )            