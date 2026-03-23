from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

CATEGORY_MAP = {
    400: "client_error",
    401: "authentication_error",
    403: "authorization_error",
    404: "not_found",
    409: "conflict",
    422: "validation_error",
    # 429: "rate_limit_error"  TODO: add when rate limiting is implemented
}

CODE_MAP = {
    400: "BAD_REQUEST",
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    409: "CONFLICT",
    422: "UNPROCESSABLE",
    # 429: "RATE_LIMIT_EXCEEDED"  TODO: add when rate limiting is implemented
}

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Convert Pydantic validation errors to 400 with consistent structured format."""
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        errors.append(f"{field}: {error['msg']}")

    return JSONResponse(
        status_code=400,
        headers={"Content-Type": "application/json"},
        content={
            "category": "Validation Error",
            "status": 400,
            "code": "INVALID_INPUT",
            "message": "; ".join(errors)
        }
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    """Convert all HTTPExceptions to consistent structured format."""
    headers = dict(exc.headers) if exc.headers else {}
    return JSONResponse(
        status_code=exc.status_code,
        headers=headers,
        content={
            "category": CATEGORY_MAP.get(exc.status_code, "server_error"),
            "status": exc.status_code,
            "code": CODE_MAP.get(exc.status_code, "INTERNAL_ERROR"),
            "message": exc.detail
        }
    )
