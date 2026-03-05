from app.repositories.base_repository import BaseRepository

class RegionsRepository(BaseRepository):
  def insert_one(self, region_code, region_text):
    self.execute(
      """
      INSERT INTO regions (region_code, region_text) 
      VALUES (%s, %s) 
      ON CONFLICT (region_code) DO NOTHING
      """,
      (region_code, region_text)
    )
      
  def get_all(self):
      return self.fetch_all(
        "SELECT * FROM regions ORDER BY region_code;"
      )

  def get_by_code(self, region_code):
      return self.fetch_one(
        "SELECT * FROM regions WHERE region_code = %s;",
        (region_code,)
      )