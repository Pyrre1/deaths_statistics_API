from fastapi import APIRouter, Depends, Query

from app.controllers.causes_controller import CausesController
from app.dependencies.connection import get_db
from app.models.cause_models import CauseDetailResponse, CausesListResponse

router = APIRouter(prefix="/causes", tags=["Causes"])

@router.get("/", response_model=CausesListResponse)
def get_causes(
    limit: int = Query(100, ge=1, le=5000, description="Number of records to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    db=Depends(get_db)):
    controller = CausesController(db)
    return controller.get_all(limit=limit, offset=offset)

@router.get("/{diagnosis_code}", response_model=CauseDetailResponse)
def get_cause(diagnosis_code: str, db=Depends(get_db)):
    controller = CausesController(db)
    return controller.get_one(diagnosis_code)
