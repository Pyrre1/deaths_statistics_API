from fastapi import HTTPException
from app.repositories.regions_repository import RegionsRepository
from app.models.region_models import RegionResponse, RegionsListResponse

class RegionsController:
  def __init__(self, db):
    self.regions_repo = RegionsRepository(db)

  def _map_to_response(self, region_data):
    return RegionResponse(
      code=region_data["region_code"],
      name=region_data["region_text"]
    )

  def get_all(self):
    regions_data = self.regions_repo.get_all()
    regions = [
      self._map_to_response(region)
      for region in regions_data
    ]

    return RegionsListResponse(
      data=regions,
      total=len(regions)
    )

  def get_one(self, region_code):
    region_data = self.regions_repo.get_by_code(region_code)
    if not region_data:
      raise HTTPException(status_code=404, detail="Region not found")
    # Transformera datan till en RegionResponse-modell
    return self._map_to_response(region_data)