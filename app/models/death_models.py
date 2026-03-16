from typing import Any

from pydantic import BaseModel, Field


# ===== DATABASE MODELS (Internal) =====
class DeathDB(BaseModel):
    year: int = Field(..., ge=1997, le=2030, description="Year of death")
    region_code: int = Field(..., description="Region code")
    sex_code: int = Field(..., ge=1, le=3, description="Sex code (1=Men, 2=Women, 3=Both or n/a)")
    age_code: int = Field(
        ..., ge=1, le=99, description="Age code (1-20 for age groups, 99 for total)"
    )
    diagnosis_code: str = Field(..., description="Diagnosis code")
    measure_code: int = Field(..., ge=1, le=2, description="Measure code (1=Count, 2=Per 100k)")
    value: float | None = Field(..., description="Death count or rate")


class DeathCreate(DeathDB):
    """Request model for creating a new death record"""

    pass  # Inherits all fields from DeathDB, which are required for creation.


class DeathUpdate(BaseModel):
    """Request model for updating an existing death record (all fields optional)"""

    year: int | None = Field(None, ge=1997, le=2030)
    region_code: int | None = None
    sex_code: int | None = Field(None, ge=1, le=3)
    age_code: int | None = Field(None, ge=1, le=99)
    diagnosis_code: str | None = None
    measure_code: int | None = Field(None, ge=1, le=2)
    value: float | None = Field(None, description="Death count or rate")


class DeathResponse(BaseModel):
    """Response model for a death record"""

    id: int
    year: int
    region_code: int
    region_name: str
    sex_code: int
    sex_label: str
    age_code: int
    age_range: str
    diagnosis_code: str
    diagnosis_name: str
    measure_code: int
    measure_label: str
    value: float | None = None
    links: dict[str, Any] = Field(..., alias="_links")

    class Config:
        populate_by_name = True
        from_attributes = True  # Allows creating from DB rows.
        json_schema_extra = {
            "example": {
                "id": 391979,
                "year": 2024,
                "region_code": 3,
                "region_name": "Uppsala län",
                "sex_code": 2,
                "sex_label": "Kvinnor",
                "age_code": 16,
                "age_range": "71-75",
                "diagnosis_code": "I00-I99",
                "diagnosis_name": "Cirkulationsorganens sjukdomar",
                "measure_code": 1,
                "measure_label": "Antal döda",
                "value": 368,
                "_links": {
                    "self": "/deaths/391979",
                    "region": "/regions/3",
                    "cause": "/causes/I00-I99",
                    "collection": "/deaths",
                },
            }
        }


class DeathsListResponse(BaseModel):
    """Response model for a list of deaths"""

    data: list[DeathResponse]
    total: int
    limit: int
    offset: int
    links: dict[str, Any] = Field(..., alias="_links")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "data": ["... list of death records ..."],
                "total": 411214,
                "limit": 100,
                "offset": 0,
                "_links": {
                    "self": "/deaths?limit=100&offset=0&measure_code=1",
                    "next": "/deaths?limit=100&offset=100&measure_code=1",
                    "prev": None,
                },
            }
        }
