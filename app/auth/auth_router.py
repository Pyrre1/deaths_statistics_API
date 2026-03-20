from fastapi import APIRouter, Depends

from app.auth.auth_models import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse
from app.auth.auth_service import AuthService
from app.dependencies.connection import get_db

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/token", response_model=TokenResponse, status_code=200)
def login(login_data: LoginRequest, db=Depends(get_db)):
    """Authenticate user and return access + refresh tokens"""
    auth_service = AuthService(db)
    return auth_service.login(login_data.username, login_data.password)


@router.post("/refresh", response_model=TokenResponse, status_code=200)
def refresh_token(refresh_data: RefreshRequest, db=Depends(get_db)):
    """Exchange a valid refresh token for a new token pair."""
    auth_service = AuthService(db)
    new_access_token, new_refresh_token, _ = auth_service.rotate_refresh_token(
        refresh_data.refresh_token
    )
    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=AuthService.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/register", status_code=201)
def register(register_data: RegisterRequest, db=Depends(get_db)):
    """Register a new user."""
    auth_service = AuthService(db)

    return auth_service.register(register_data.username, register_data.password)
