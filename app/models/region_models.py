
from pydantic import BaseModel, Field


# ===== DATABASE MODELS (Internal) =====
class RegionDB(BaseModel):
    region_code: int
    region_text: str

    class Config:
        from_attributes = True # Allows creating from DB rows.

# ===== API RESPONSE MODELS (External) =====
class RegionResponse(BaseModel):
    """Single region basic info"""
    id: int = Field(..., description="Unique region identifier")
    name: str = Field(..., description="Region name")

    class Config:
      json_schema_extra = {
        "example": {
          "id": 1,
          "name": "Stockholm"
        }
      }

class RegionStatistics(BaseModel):
    """Statistics for a region"""
    total_deaths: int
    avg_age_range: str = Field(
      ...,
      description="Average age range of deaths in the region"
    )
    timeframe: dict = Field(
      ...,
      description="Timeframe for these statistics"
    )
    # top_causes: Optional[list[str]] = None # TODO: Implement this later.

    class Config:
      json_schema_extra = {
        "example": {
          "total_deaths": 1234,
          "avg_age_range": "75-79",
          "timeframe": {
            "from_year": 2010,
            "to_year": 2020
            }
          # "top_causes": ["Heart Disease", "Cancer", "Stroke"] # TODO: Implement this later.
        }
      }

class RegionDetailResponse(BaseModel):
    """Detailed region with statistics"""
    id: int
    name: str
    statistics: RegionStatistics | None = None
    # TODO: add _links, and HATEOAS later.

class RegionsListResponse(BaseModel):
    """List of all regions"""
    data: list[RegionResponse]
    total: int

    class Config:
      json_schema_extra = {
        "example": {
          "data": [
            {"id": 0, "name": "Riket"},
            {"id": 1, "name": "Stockholm"},
            {"id": 2, "name": "Gothenburg"}
          ],
          "total": 3
        }
      }
    # TODO: add pagination and HATEOAS links later.
