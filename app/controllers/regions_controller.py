from fastapi import HTTPException
from app.repositories.regions_repository import RegionsRepository
from app.models.region_models import RegionResponse, RegionsListResponse, RegionDetailResponse
from app.services.region_service import RegionService

class RegionsController:
  def __init__(self, db):
    self.regions_repo = RegionsRepository(db)
    self.region_service = RegionService(db)

  def _map_to_response(self, region_data):
    return RegionResponse(
      id=region_data["region_code"],
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
    
    # Get statistics
    statistics = self.region_service.get_region_statistics(region_code)

    # Return detailed response including statistics
    return RegionDetailResponse(
      id=region_data["region_code"],
      name=region_data["region_text"],
      statistics=statistics
    )