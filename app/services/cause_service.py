from fastapi import HTTPException

from app.models.cause_models import CauseStatistics
from app.repositories.causes_repository import CausesRepository
from app.repositories.deaths_repository import DeathsRepository


class CauseService:
    def __init__(self, db):
        self.causes_repo = CausesRepository(db)
        self.deaths_repo = DeathsRepository(db)

    def get_cause_statistics(self, diagnosis_code):
        # Verify cause exists
        cause = self.causes_repo.get_by_code(diagnosis_code)
        if not cause:
            raise HTTPException(status_code=404, detail="Cause not found")

        # Calculate statistics
        total_deaths = self.deaths_repo.count_by_cause(diagnosis_code)
        avg_age_range = self.deaths_repo.average_age_by_cause(diagnosis_code)
        year_range = self.deaths_repo.get_year_range_by_cause(diagnosis_code)

        # Return Pydantic model with statistics
        return CauseStatistics(
            total_deaths=total_deaths,
            avg_age_range=avg_age_range,
            timeframe={"from_year": year_range["min_year"], "to_year": year_range["max_year"]},
        )
