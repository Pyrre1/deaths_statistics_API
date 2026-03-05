from fastapi import APIRouter, Depends
from app.controllers.regions_controller import RegionsController
from app.dependencies.connection import get_db

router = APIRouter(prefix="/regions", tags=["Regions"])

@router.get("/")
def get_regions(db=Depends(get_db)):
    controller = RegionsController(db)
    return controller.get_all()

@router.get("/{region_code}")
def get_region(region_code: int, db=Depends(get_db)):
    controller = RegionsController(db)
    return controller.get_one(region_code)