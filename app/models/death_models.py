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

    class Config:
        from_attributes = True  # Allows creating from DB rows.


class DeathsListResponse(BaseModel):
    """Response model for a list of deaths"""

    data: list[DeathResponse]
    total: int
    limit: int
    offset: int
