from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from app.auth.auth_router import router as auth_router
from app.config import API_VERSION, BASE_URL
from app.routers.causes_router import router as causes_router
from app.routers.deaths_router import router as deaths_router
from app.routers.regions_router import router as regions_router
from app.utils.error_handlers import http_exception_handler, validation_exception_handler

# Global limiter instance - imported by routers that need per-route limits
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

app = FastAPI(root_path="/api", redirect_slashes=False)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore
app.add_middleware(SlowAPIMiddleware)

app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore
app.add_exception_handler(HTTPException, http_exception_handler)  # type: ignore

v1_router = APIRouter(prefix=f"/{API_VERSION}")
v1_router.include_router(regions_router)
v1_router.include_router(deaths_router)
v1_router.include_router(auth_router)
v1_router.include_router(causes_router)

app.include_router(v1_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:3000",
        "http://192.168.0.61:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    """API root — returns available endpoints and documentation link."""
    return {
        "message": "Welcome to the Assignment Swedish Death Statistics API",
        "documentation": f"{BASE_URL}/docs",
        "version": "1.0.0",
        "CRUD_endpoints": f"{BASE_URL}/{API_VERSION}/deaths",
        "Read only endpoint 1": f"{BASE_URL}/{API_VERSION}/causes",
        "Read only endpoint 2": f"{BASE_URL}/{API_VERSION}/regions",
    }
