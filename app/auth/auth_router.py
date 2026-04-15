import os

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.auth.auth_models import (
    LoginRequest,
    OAuthRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)
from app.auth.auth_service import AuthService
from app.dependencies.auth import get_current_user
from app.dependencies.connection import get_db

router = APIRouter(prefix="/auth", tags=["Authentication"])
limiter = Limiter(key_func=get_remote_address)  # Create a limiter instance for this router


@router.post("/token", response_model=TokenResponse, status_code=200)
@limiter.limit("10/minute")
def login(request: Request, login_data: LoginRequest, db=Depends(get_db)):
    """Authenticate user and return access + refresh tokens"""
    auth_service = AuthService(db)
    return auth_service.login(login_data.username, login_data.password)


@router.post("/refresh", response_model=TokenResponse, status_code=200)
@limiter.limit("20/minute")
def refresh_token(request: Request, refresh_data: RefreshRequest, db=Depends(get_db)):
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
@limiter.limit("5/minute")
def register(request: Request, register_data: RegisterRequest, db=Depends(get_db)):
    """Register a new user."""
    auth_service = AuthService(db)

    return auth_service.register(register_data.username, register_data.password)


@router.post("/oauth", response_model=TokenResponse, status_code=200)
@limiter.limit("10/minute")
def oauth_login(
    request: Request,
    oauth_data: OAuthRequest,
    db=Depends(get_db),
    x_internal_secret: str = Header(...),
):
    """Find-or-create a GitHub OAuth user and return tokens."""
    if x_internal_secret != os.getenv("INTERNAL_SECRET"):
        raise HTTPException(status_code=401, detail="Invalid internal secret")

    auth_service = AuthService(db)
    return auth_service.oauth_login(oauth_data.github_id, oauth_data.email, oauth_data.name)


@router.delete("/delete", status_code=204)
def delete_current_user(current_user=Depends(get_current_user), db=Depends(get_db)):
    """Delete the currently authenticated user's account."""
    auth_service = AuthService(db)
    auth_service.delete_user(int(current_user["sub"]))
    return None
