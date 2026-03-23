from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError

from app.auth.auth_router import router as auth_router
from app.routers.causes_router import router as causes_router
from app.routers.deaths_router import router as deaths_router
from app.routers.regions_router import router as regions_router
from app.utils.error_handlers import http_exception_handler, validation_exception_handler

app = FastAPI()

app.add_exception_handler(RequestValidationError, validation_exception_handler) # type: ignore
app.add_exception_handler(HTTPException, http_exception_handler) # type: ignore

app.include_router(regions_router)
app.include_router(deaths_router)
app.include_router(auth_router)
app.include_router(causes_router)
