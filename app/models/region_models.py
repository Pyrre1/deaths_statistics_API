from pydantic import BaseModel, Field
from typing import Optional

# ===== DATABASE MODELS (Internal) =====
class RegionDB(BaseModel):
    region_code: int
    region_text: str

    class Config:
        from_attributes = True # Allows creating from DB rows.

# ===== API RESPONSE MODELS (External) =====
class RegionResponse(BaseModel):
    """Single region basic info"""
    code: int = Field(..., description="Unique region identifier")
    name: str = Field(..., description="Region name")

    class Config:
      json_schema_extra = {
        "example": {
          "code": 1,
          "name": "Stockholm"
        }
      }

class RegionStatistics(BaseModel):
    """Statistics for a region"""
    total_deaths: int
    avg_age: float
    top_causes: Optional[list[str]] = None # TODO: Implement this later.

class RegionDetailResponse(BaseModel):
    """Detailed region with statistics"""
    code: int
    name: str
    statistics: Optional[RegionStatistics] = None
    # TODO: add _links, and HATEOAS later.

class RegionsListResponse(BaseModel):
    """List of all regions"""
    data: list[RegionResponse]
    total: int
    # TODO: add pagination and HATEOAS links later.





