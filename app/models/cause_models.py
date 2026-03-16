from typing import Any

from pydantic import BaseModel, Field


# ===== DATABASE MODELS (Internal) =====
class CauseDB(BaseModel):
    diagnosis_code: str
    diagnosis_text: str

    class Config:
        from_attributes = True  # Allows creating from DB rows.


# ===== API RESPONSE MODELS (External) =====
class CauseResponse(BaseModel):
    """Single cause of death"""

    code: str = Field(..., description="Diagnosis code")
    name: str = Field(..., description="Cause of death description")
    links: dict[str, Any] = Field(..., alias="_links")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "code": "I21",
                "name": "Akut hjärtinfarkt",
                "_links": {
                    "self": "/causes/I21",
                    "deaths": "/deaths?diagnosis_code=I21&measure_code=1",
                },
            }
        }


class CauseStatistics(BaseModel):
    """Statistics for a specific cause"""

    measure_code: int = Field(1, description="1=Count, 2=Per 100k")
    measure_label: str = Field("Antal döda", description="Human-readable measure")
    value: int = Field(..., description="Total deaths for this cause")
    avg_age_range: str = Field(..., description="Average age range of deaths for this cause")
    timeframe: dict = Field(..., description="Timeframe for the statistics")


class CauseDetailResponse(BaseModel):
    """Detailed cause with statistics"""

    code: str
    name: str
    statistics: CauseStatistics | None = None
    links: dict[str, Any] = Field(..., alias="_links")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "code": "I61",
                "name": "Hjärnblödning",
                "statistics": {
                    "measure_code": 1,
                    "measure_label": "Antal döda",
                    "value": 866,
                    "avg_age_range": "75-79",
                    "timeframe": {"from_year": 2022, "to_year": 2024},
                },
                "_links": {
                    "self": "/causes/I61",
                    "deaths": "/deaths?diagnosis_code=I61&measure_code=1",
                    "collection": "/causes",
                },
            }
        }


class CausesListResponse(BaseModel):
    """List of all causes"""

    data: list[CauseResponse]
    total: int
    limit: int
    offset: int
    links: dict[str, Any] = Field(..., alias="_links")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "data": [
                    {
                        "code": "I21",
                        "name": "Akut hjärtinfarkt",
                        "_links": {
                            "self": "/causes/I21",
                            "deaths": "/deaths?diagnosis_code=I21&measure_code=1",
                        },
                    },
                    {
                        "code": "I61",
                        "name": "Hjärnblödning",
                        "_links": {
                            "self": "/causes/I61",
                            "deaths": "/deaths?diagnosis_code=I61&measure_code=1",
                        },
                    },
                ],
                "total": 1948,
                "limit": 100,
                "offset": 0,
                "_links": {
                    "self": "/causes?limit=100&offset=0",
                    "next": "/causes?limit=100&offset=100",
                    "prev": None,
                },
            }
        }
