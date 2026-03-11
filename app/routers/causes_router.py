from fastapi import APIRouter, Depends

from app.controllers.causes_controller import CausesController
from app.dependencies.connection import get_db
from app.models.cause_models import CauseDetailResponse, CausesListResponse

router = APIRouter(prefix="/causes", tags=["Causes"])

@router.get("/", response_model=CausesListResponse)
def get_causes(db=Depends(get_db)):
    controller = CausesController(db)
    return controller.get_all()

@router.get("/{diagnosis_code}", response_model=CauseDetailResponse)
def get_cause(diagnosis_code: str, db=Depends(get_db)):
    controller = CausesController(db)
    return controller.get_one(diagnosis_code)
