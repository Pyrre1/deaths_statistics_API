from fastapi import HTTPException
from app.repositories.regions_repository import RegionsRepository

class RegionsController:
  def __init__(self, db):
    self.regions_repo = RegionsRepository(db)

  def get_all(self):
    return self.regions_repo.get_all()

  def get_one(self, region_code):
    region = self.regions_repo.get_by_code(region_code)
    if not region:
      raise HTTPException(status_code=404, detail="Region not found")
    return region