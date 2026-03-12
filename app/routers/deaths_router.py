from fastapi import APIRouter, Depends

from app.controllers.deaths_controller import DeathsController
from app.dependencies.connection import get_db
from app.models.death_models import DeathCreate, DeathResponse, DeathsListResponse, DeathUpdate

router = APIRouter(prefix="/deaths", tags=["Deaths"])


@router.post("/", response_model=DeathResponse, status_code=201)
def create_death(death_data: DeathCreate, db=Depends(get_db)):
    """Create a new death record"""
    controller = DeathsController(db)
    return controller.create(death_data)


@router.get("/", response_model=DeathsListResponse)
def get_deaths(limit: int = 100, offset: int = 0, db=Depends(get_db)):
    """Get all death records with pagination"""
    controller = DeathsController(db)
    return controller.get_all(limit=limit, offset=offset)


@router.get("/{death_id}", response_model=DeathResponse)
def get_death(death_id: int, db=Depends(get_db)):
    """Get a single death record by ID"""
    controller = DeathsController(db)
    return controller.get_one(death_id)


@router.put("/{death_id}", response_model=DeathResponse)
def update_death(death_id: int, death_data: DeathUpdate, db=Depends(get_db)):
    """Update an existing death record"""
    controller = DeathsController(db)
    return controller.update(death_id, death_data)


@router.delete("/{death_id}")
def delete_death(death_id: int, db=Depends(get_db)):
    """Delete a death record by ID"""
    controller = DeathsController(db)
    return controller.delete(death_id)
