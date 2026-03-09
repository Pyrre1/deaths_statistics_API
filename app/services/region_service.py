class RegionService:
  def __init__(self, db):
    self.regions_repo = RegionsRepository(db)
    self.deaths_repo = DeathsRepository(db)

  def get_regions_statistics(self, region_code):
    region = self.regions_repo.get_by_code(region_code)
    if not region:
      raise HTTPException(status_code=404, detail="Region not found")
    
    total_deaths = self.deaths_repo.count_by_region(region_code)
    avg_age = self.deaths_repo.average_age_by_region(region_code)
    
    return {
      total_deaths=total_deaths
    }