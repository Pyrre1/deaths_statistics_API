from fastapi import APIRouter, Depends, Query

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
def get_deaths(
    from_year: int | None = Query(None, ge=1997, le=2030, description="Start year (inclusive)"),
    to_year: int | None = Query(None, ge=1997, le=2030, description="End year (inclusive)"),
    region_code: int | None = Query(None, description="Filter by region code"),
    sex_code: int | None = Query(None, ge=1, le=3, description="1=Men, 2=Women, 3=Both"),
    age_code: int | None = Query(
        None, ge=1, le=99, description="1-20 for age groups, 99 for total"
    ),
    diagnosis_code: str | None = Query(None, description="Filter by diagnosis code"),
    measure_code: int | None = Query(None, ge=1, le=2, description="1=Count, 2=Per 100k"),
    order_by: str = Query("id", description="Field to order by (e.g. year, region_code)"),
    direction: str = Query("asc", pattern="^(asc|desc)$", description="Sort direction"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    db=Depends(get_db),
):
    """Get death records with optional filtering and pagination"""
    controller = DeathsController(db)
    return controller.find(
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
