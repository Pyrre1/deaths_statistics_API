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

    class Config:
        json_schema_extra = {"example": {"code": "99", "name": "Samtliga dödsorsaker"}}


class CauseStatistics(BaseModel):
    """Statistics for a specific cause"""

    measure_code: int = Field(1, description="1=Count, 2=Per 100k")
    measure_label: str = Field("Antal döda", description="Human-readable measure")
    value: int = Field(..., description="Total deaths for this cause")
    avg_age_range: str = Field(..., description="Average age range of deaths for this cause")
    timeframe: dict = Field(..., description="Timeframe for the statistics")

    class Config:
        json_schema_extra = {
            "example": {
                "value": 1234,
                "avg_age_range": "75-79",
                "timeframe": {"from_year": 2022, "to_year": 2024},
            }
        }


class CauseDetailResponse(BaseModel):
    """Detailed cause with statistics"""

    code: str
    name: str
    statistics: CauseStatistics | None = None


class CausesListResponse(BaseModel):
    """List of all causes"""

    data: list[CauseResponse]
    total: int
    limit: int
    offset: int

    class Config:
        json_schema_extra = {
            "example": {
                "total": 5,
                "data": [
                    {"code": "99", "name": "Samtliga dödsorsaker"},
                    {"code": "I21", "name": "Akut hjärtinfarkt"},
                    {"code": "C34", "name": "Malign tumör i bronk och lunga"},
                    {"code": "I63", "name": "Cerebral infarkt"},
                    {"code": "J18", "name": "Pneumoni orsakad av ospecificerad mikroorganism"},
                ],
                "limit": 100,
                "offset": 0
            }
        }
