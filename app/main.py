from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.auth.auth_router import router as auth_router
from app.routers.causes_router import router as causes_router
from app.routers.deaths_router import router as deaths_router
from app.routers.regions_router import router as regions_router

app = FastAPI()

app.include_router(regions_router)
app.include_router(deaths_router)
app.include_router(auth_router)
app.include_router(causes_router)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Override FastAPI's default validation error handler to return a 400 status code instead of 422."""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": "->".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
        })
    return JSONResponse(
        status_code=400,
        content={"error": "; ".join(f"{err['field']}: {err['message']}" for err in errors)},
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Override FastAPI's default HTTPException handler to ensure all errors return a consistent JSON format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
    )
