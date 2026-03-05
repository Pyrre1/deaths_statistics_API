from fastapi import FastAPI
from app.routers.regions_router import router as regions_router

app = FastAPI()

app.include_router(regions_router)