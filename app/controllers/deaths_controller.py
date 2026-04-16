from fastapi import HTTPException
from psycopg.errors import ForeignKeyViolation

from app.config import API_VERSION, BASE_URL
from app.models.death_models import DeathCreate, DeathResponse, DeathsListResponse, DeathUpdate
from app.repositories.deaths_repository import DeathsRepository
from app.utils.links import pagination_links


class DeathsController:
    def __init__(self, db):
        self.deaths_repo = DeathsRepository(db)

    def _map_to_response(self, death_data):
        """Map a database row to a DeathResponse with HATEOAS links."""
        base = f"{BASE_URL}/{API_VERSION}/deaths/{death_data['id']}"
        return DeathResponse(
            **{key: value for key, value in death_data.items()},
            _links={
                "self": {"href": base, "method": "GET"},
                "update": {"href": base, "method": "PUT"},
                "delete": {"href": base, "method": "DELETE"},
                "collection": {"href": f"{BASE_URL}/{API_VERSION}/deaths", "method": "GET"},
                "region": {
                    "href": f"{BASE_URL}/{API_VERSION}/regions/{death_data['region_code']}",
                    "method": "GET",
                },
                "cause": {
                    "href": f"{BASE_URL}/{API_VERSION}/causes/{death_data['diagnosis_code']}",
                    "method": "GET",
                },
            },
        )

    def create(self, death_data: DeathCreate) -> DeathResponse:
        """Create a new death record"""
        try:
            new_id = self.deaths_repo.insert_one(
                year=death_data.year,
                region_code=death_data.region_code,
                sex_code=death_data.sex_code,
                age_code=death_data.age_code,
                diagnosis_code=death_data.diagnosis_code,
                measure_code=death_data.measure_code,
                value=death_data.value,
            )
        except ForeignKeyViolation:
            raise HTTPException(
                status_code=400, detail="Invalid reference"
            )

        return self.get_one(new_id)

    def find(
        self,
        from_year=None,
        to_year=None,
        region_code=None,
        sex_code=None,
        age_code=None,
        diagnosis_code=None,
        measure_code=None,
        order_by="id",
        direction="asc",
        limit=100,
        offset=0,
    ) -> DeathsListResponse:
        """Filter and paginate death records, mapping results to DeathsListResponse with HATEOAS links."""
        try:
            result = self.deaths_repo.find(
                from_year=from_year,
                to_year=to_year,
                region_code=region_code,
                sex_code=sex_code,
                age_code=age_code,
                diagnosis_code=diagnosis_code,
                measure_code=measure_code,
                order_by=order_by,
                direction=direction,
                limit=limit,
                offset=offset,
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        deaths = [self._map_to_response(death) for death in result["items"]]

        links = pagination_links(
            f"{BASE_URL}/{API_VERSION}/deaths",
            offset=offset,
            limit=limit,
            total=result["total"],
            from_year=from_year,
            to_year=to_year,
            region_code=region_code,
            sex_code=sex_code,
            age_code=age_code,
            diagnosis_code=diagnosis_code,
            measure_code=measure_code,
        )
        links["create"] = {"href": f"{BASE_URL}/{API_VERSION}/deaths", "method": "POST"}

        return DeathsListResponse(
            data=deaths,
            total=result["total"],
            limit=limit,
            offset=offset,
            _links=links,
        )

    def get_one(self, death_id: int):
        """Get a single death record by ID"""
        death_data = self.deaths_repo.get_by_id(death_id)
        if not death_data:
            raise HTTPException(status_code=404, detail="Death record not found")

        return self._map_to_response(death_data)

    def update(self, death_id: int, death_data: DeathUpdate):
        """Update an existing death record"""
        # Only include fields that are provided (not None)
        update_data = death_data.model_dump(exclude_unset=True)

        if not update_data:
            raise HTTPException(status_code=400, detail="No fields provided for update")

        try:
            updated = self.deaths_repo.update_one(death_id, **update_data)
        except ForeignKeyViolation:
            raise HTTPException(
                status_code=400, detail="Invalid reference"
            )

        if not updated:
            raise HTTPException(status_code=404, detail="Death record not found")

        return self._map_to_response(updated)

    def delete(self, death_id: int):
        """Delete a death record by ID"""
        deleted = self.deaths_repo.delete_one(death_id)

        if not deleted:
            raise HTTPException(status_code=404, detail="Death record not found")

        return {"message": "Death record deleted successfully", "id": death_id}
