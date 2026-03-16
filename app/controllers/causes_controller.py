from fastapi import HTTPException

from app.models.cause_models import CauseDetailResponse, CauseResponse, CausesListResponse
from app.repositories.causes_repository import CausesRepository
from app.services.cause_service import CauseService
from app.utils.links import pagination_links


class CausesController:
    def __init__(self, db):
        self.causes_repo = CausesRepository(db)
        self.cause_service = CauseService(db)

    def _map_to_response(self, cause_data):
        """Transform database model to API response"""
        return CauseResponse(
            code=cause_data["diagnosis_code"],
            name=cause_data["diagnosis_text"],
            _links={
                "self": f"/causes/{cause_data['diagnosis_code']}",
                "deaths": f"/deaths?diagnosis_code={cause_data['diagnosis_code']}&measure_code=1",
            },
        )

    def get_all(self, limit=100, offset=0):
        """Get all causes, with pagination"""
        causes_data = self.causes_repo.get_all(limit=limit, offset=offset)
        total = self.causes_repo.count_all()
        causes = [self._map_to_response(cause) for cause in causes_data]

        return CausesListResponse(
            data=causes,
            total=total,
            limit=limit,
            offset=offset,
            _links=pagination_links("/causes", offset=offset, limit=limit, total=total),
        )

    def get_one(self, diagnosis_code):
        """Get single cause with statistics"""
        cause_data = self.causes_repo.get_by_code(diagnosis_code)
        if not cause_data:
            raise HTTPException(status_code=404, detail="Cause not found")

        # Get statistics
        statistics = self.cause_service.get_cause_statistics(diagnosis_code)

        # Return detailed response including statistics
        return CauseDetailResponse(
            code=cause_data["diagnosis_code"],
            name=cause_data["diagnosis_text"],
            statistics=statistics,
            _links={
                "self": f"/causes/{diagnosis_code}",
                "deaths": f"/deaths?diagnosis_code={diagnosis_code}&measure_code=1",
                "collection": "/causes",
            },
        )
