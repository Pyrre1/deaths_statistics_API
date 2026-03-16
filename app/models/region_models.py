from pydantic import BaseModel, Field


# ===== DATABASE MODELS (Internal) =====
class RegionDB(BaseModel):
    region_code: int
    region_text: str

    class Config:
        from_attributes = True  # Allows creating from DB rows.


# ===== API RESPONSE MODELS (External) =====
class RegionResponse(BaseModel):
    """Single region basic info"""

    id: int = Field(..., description="Region code")
    name: str = Field(..., description="Region name")
    links: dict[str, str] | None = Field(..., alias="_links")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Stockholms län",
                "_links": {"self": "/regions/1", "deaths": "/deaths?region_code=1&measure_code=1"},
            }
        }


class RegionStatistics(BaseModel):
    """Statistics for a region"""

    measure_code: int = Field(1, description="1=Count, 2=Per 100k")
    measure_label: str = Field("Antal döda", description="Human-readable measure")
    value: int = Field(..., description="Total deaths in this region")
    avg_age_range: str = Field(..., description="Average age range of deaths in the region")
    timeframe: dict = Field(..., description="Timeframe for these statistics")
    # top_causes: Optional[list[str]] = None # TODO: Implement this later.


class RegionDetailResponse(BaseModel):
    """Detailed region with statistics"""

    id: int
    name: str
    statistics: RegionStatistics | None = None
    links: dict[str, str] | None = Field(..., alias="_links")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Stockholms län",
                "statistics": {
                    "measure_code": 1,
                    "measure_label": "Antal döda",
                    "value": 15615,
                    "avg_age_range": "65-69",
                    "timeframe": {"from_year": 2022, "to_year": 2024},
                },
                "_links": {
                    "self": "/regions/1",
                    "deaths": "/deaths?region_code=1&measure_code=1",
                    "collection": "/regions",
                },
            }
        }


class RegionsListResponse(BaseModel):
    """List of all regions"""

    data: list[RegionResponse]
    total: int
    links: dict[str, str] | None = Field(..., alias="_links")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "data": [
                    {
                        "id": 0,
                        "name": "Riket",
                        "_links": {
                            "self": "/regions/0",
                            "deaths": "/deaths?region_code=0&measure_code=1",
                        },
                    },
                    {
                        "id": 1,
                        "name": "Stockholms län",
                        "_links": {
                            "self": "/regions/1",
                            "deaths": "/deaths?region_code=1&measure_code=1",
                        },
                    },
                ],
                "total": 22,
                "_links": {"self": "/regions"},
            }
        }
