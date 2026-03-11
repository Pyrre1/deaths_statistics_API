from fastapi import FastAPI

from app.routers.causes_router import router as causes_router
from app.routers.regions_router import router as regions_router

app = FastAPI()

app.include_router(regions_router)
app.include_router(causes_router)
