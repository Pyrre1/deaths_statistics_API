from fastapi import APIRouter, Depends

from app.controllers.regions_controller import RegionsController
from app.dependencies.connection import get_db
from app.models.region_models import RegionDetailResponse, RegionsListResponse

router = APIRouter(prefix="/regions", tags=["Regions"])


@router.get("", response_model=RegionsListResponse)
def get_regions(db=Depends(get_db)):
    controller = RegionsController(db)
    return controller.get_all()


@router.get("/{region_code}", response_model=RegionDetailResponse)
def get_region(region_code: int, db=Depends(get_db)):
    controller = RegionsController(db)
    return controller.get_one(region_code)
