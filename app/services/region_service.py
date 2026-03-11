from fastapi import HTTPException
from app.repositories.regions_repository import RegionsRepository
from app.repositories.deaths_repository import DeathsRepository
from app.models.region_models import RegionStatistics

class RegionService:
  def __init__(self, db):
    self.regions_repo = RegionsRepository(db)
    self.deaths_repo = DeathsRepository(db)

  def get_region_statistics(self, region_code):
    # Verify region exists
    region = self.regions_repo.get_by_code(region_code)
    if not region:
      raise HTTPException(status_code=404, detail="Region not found")
    
    # Calculate statistics
    total_deaths = self.deaths_repo.count_by_region(region_code)
    avg_age_range = self.deaths_repo.average_age_by_region(region_code)
    year_range = self.deaths_repo.get_year_range_by_region(region_code)
    
    # Return Pydantic model with statistics
    return RegionStatistics(
      total_deaths=total_deaths,
      avg_age_range=avg_age_range,
      timeframe={
        "from_year": year_range["min_year"],
        "to_year": year_range["max_year"]
      }
    )