from fastapi import Depends, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.auth_service import AuthService
from app.dependencies.connection import get_db

bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme), db=Depends(get_db)
) -> dict:
    """
    FastAPI dependency - extracts and verifies the Bearer token.
    Inject into any endpoint that requires authentication.
    """

    auth_service = AuthService(db)
    return auth_service.verify_access_token(credentials.credentials)
