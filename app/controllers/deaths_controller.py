from fastapi import HTTPException

from app.models.death_models import DeathCreate, DeathResponse, DeathsListResponse, DeathUpdate
from app.repositories.deaths_repository import DeathsRepository


class DeathsController:
    def __init__(self, db):
        self.deaths_repo = DeathsRepository(db)

    def create(self, death_data: DeathCreate):
        """Create a new death record"""
        new_id = self.deaths_repo.insert_one(
            year=death_data.year,
            region_code=death_data.region_code,
            sex_code=death_data.sex_code,
            age_code=death_data.age_code,
            diagnosis_code=death_data.diagnosis_code,
            measure_code=death_data.measure_code,
            deaths_count=death_data.deaths_count,
        )

        return self.get_one(new_id)

    def get_all(self, limit=100, offset=0):
        """Get all death records with pagination"""
        result = self.deaths_repo.get_all(limit=limit, offset=offset)

        deaths = [DeathResponse(**death) for death in result["items"]]

        return DeathsListResponse(
            data=deaths,
            total=result["total"],
            limit=limit,
            offset=offset,
        )

    def get_one(self, death_id: int):
        """Get a single death record by ID"""
        death_data = self.deaths_repo.get_by_id(death_id)
        if not death_data:
            raise HTTPException(status_code=404, detail="Death record not found")

        return DeathResponse(**death_data)

    def update(self, death_id: int, death_data: DeathUpdate):
        """Update an existing death record"""
        # Only include fields that are provided (not None)
        update_data = death_data.model_dump(exclude_unset=True)

        if not update_data:
            raise HTTPException(status_code=400, detail="No fields provided for update")

        updated = self.deaths_repo.update_one(death_id, **update_data)

        if not updated:
            raise HTTPException(status_code=404, detail="Death record not found")

        return DeathResponse(**updated)

    def delete(self, death_id: int):
        """Delete a death record by ID"""
        deleted = self.deaths_repo.delete_one(death_id)

        if not deleted:
            raise HTTPException(status_code=404, detail="Death record not found")

        return {"message": "Death record deleted successfully", "id": death_id}
