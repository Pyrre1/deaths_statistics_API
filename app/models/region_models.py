from pydantic import BaseModel
from typing import Optional

# Models for the regions table in the database (internal)
class RegionDB(BaseModel):
    region_code: int
    region_text: str

# Model for the API response when fetching all regions (external)
class RegionListResponse(BaseModel):
    data: list[RegionResponse]
    total: int
    # TODO: add HATEOAS, calculated data, etc.
    # HATEOAS to specific region.
    # pagination if needed (only 22 there)


# Model for the API response when fetching one region (external)
class RegionResponse(BaseModel):
    code: int
    name: str
    statistics: Optional[RegionStatistics]

    # TODO: add HATEOAS, calculated data, etc.
    # RegionStatistics: {
    # top_three_causes: Optional[List[CauseResponse]]
    # oldest_death: Optional[DeathResponse]
    # youngest_death: Optional[DeathResponse]
    # average_age: Optional[float] 
    #}
    # Links to prev/next region
    # Link to causes (other read only)
    # Link to deaths in this region? (out of scope?)


