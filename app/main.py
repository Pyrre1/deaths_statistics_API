from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from app.auth.auth_router import router as auth_router
from app.routers.causes_router import router as causes_router
from app.routers.deaths_router import router as deaths_router
from app.routers.regions_router import router as regions_router
from app.utils.error_handlers import http_exception_handler, validation_exception_handler

# Global limiter instance - imported by routers that need per-route limits
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

app = FastAPI(root_path="/api", redirect_slashes=False)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler) # type: ignore
app.add_middleware(SlowAPIMiddleware)

app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore
app.add_exception_handler(HTTPException, http_exception_handler)  # type: ignore

app.include_router(regions_router)
app.include_router(deaths_router)
app.include_router(auth_router)
app.include_router(causes_router)


@app.get("/")
def root():
    """API root — returns available endpoints and documentation link."""
    return {
        "message": "Welcome to the Assignment Swedish Death Statistics API",
        "documentation": "https://cu1034.camp.lnu.se/api/docs",
        "version": "1.0.0",
        "CRUD_endpoints": "https://cu1034.camp.lnu.se/api/deaths",
        "Read only endpoint 1": "https://cu1034.camp.lnu.se/api/causes",
        "Read only endpoint 2": "https://cu1034.camp.lnu.se/api/regions",
    }
