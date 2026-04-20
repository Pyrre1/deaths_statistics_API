from fastapi import HTTPException

from app.config import API_VERSION, BASE_URL
from app.models.region_models import RegionDetailResponse, RegionResponse, RegionsListResponse
from app.repositories.regions_repository import RegionsRepository
from app.services.region_service import RegionService


class RegionsController:
    def __init__(self, db):
        self.regions_repo = RegionsRepository(db)
        self.region_service = RegionService(db)

    def _map_to_response(self, region_data):
        """Transform database model to API response"""
        region_code = region_data["region_code"]
        return RegionResponse(
            id=region_data["region_code"],
            name=region_data["region_text"],
            _links={
                "self": f"{BASE_URL}/{API_VERSION}/regions/{region_code}",
                "deaths": f"{BASE_URL}/{API_VERSION}/deaths?region_code={region_code}&measure_code=1",
            },
        )

    def get_all(self):
        """Get all regions"""
        regions_data = self.regions_repo.get_all()
        regions = [self._map_to_response(region) for region in regions_data]

        return RegionsListResponse(
            data=regions,
            total=len(regions),
            _links={"self": f"{BASE_URL}/{API_VERSION}/regions"},
        )

    def get_one(self, region_code):
        """Get single region with statistics"""
        region_data = self.regions_repo.get_by_code(region_code)
        if not region_data:
            raise HTTPException(status_code=404, detail="Region not found")

        # Get statistics
        statistics = self.region_service.get_region_statistics(region_code)

        # Return detailed response including statistics
        return RegionDetailResponse(
            id=region_data["region_code"],
            name=region_data["region_text"],
            statistics=statistics,
            _links={
                "self": f"{BASE_URL}/{API_VERSION}/regions/{region_code}",
                "deaths": f"{BASE_URL}/{API_VERSION}/deaths?region_code={region_code}&measure_code=1",
                "collection": f"{BASE_URL}/{API_VERSION}/regions",
            },
        )
