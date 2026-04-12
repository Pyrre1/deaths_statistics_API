import hashlib
import os
import secrets
from datetime import UTC, datetime, timedelta

import bcrypt
import jwt
from fastapi import HTTPException

from app.repositories.users_repository import RefreshTokenRepository, UsersRepository


class AuthService:
    """Handles authentication logic - password verification, token creation and validation"""

    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", 7))
    ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    SECRET_KEY = os.getenv("JWT_SECRET_KEY")

    def __init__(self, db):
        self.users_repo = UsersRepository(db)
        self.refresh_token_repo = RefreshTokenRepository(db)

    # -- Password helpers --#
    def hash_password(self, plain_password: str) -> str:
        """Hash a plaintext password using bcrypt"""
        return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plaintext password against a hashed password"""
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

    # -- Token creation --#
    def create_access_token(self, user_id: int, username: str) -> str:
        """Create a short-lived signed JWT access tokenb."""
        expites_at = datetime.now(UTC) + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {
            "sub": str(user_id),
            "username": username,
            "exp": expites_at,
            "type": "access",
        }
        return jwt.encode(payload, self.SECRET_KEY, algorithm=self.ALGORITHM)

    def create_refresh_token(self, user_id: int) -> tuple[str, datetime]:
        """Create a long-lived signed JWT refresh token and store its hash in the database."""

        expires_at = datetime.now(UTC) + timedelta(days=self.REFRESH_TOKEN_EXPIRE_DAYS)
        payload = {
            "sub": str(user_id),
            "exp": expires_at,
            "type": "refresh",
            "jti": secrets.token_hex(16),  # Unique identifier for the token (for revocation)
        }

        raw_token = jwt.encode(payload, self.SECRET_KEY, algorithm=self.ALGORITHM)
        token_hash = self._hash_token(raw_token)

        self.refresh_token_repo.save_token(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        return raw_token, expires_at

    # -- Token verification --#
    def verify_access_token(self, token: str) -> dict:
        """Decode and verify a JWT access token. Raises 401 if invalid or expired."""
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Access token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid access token")

        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")

        return payload

    def rotate_refresh_token(self, raw_refresh_token: str) -> tuple[str, str, datetime]:
        """Validate an incoming refresh token, revoke it, issue a new pair. Returns (new_access_token, new_refresh_token, new_refresh_expires_at). Raises 401 if the token is invalid, expired or not in the database"""
        try:
            payload = jwt.decode(raw_refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Refresh token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")

        token_hash = self._hash_token(raw_refresh_token)
        stored_token = self.refresh_token_repo.get_by_hash(token_hash)

        if not stored_token:
            raise HTTPException(status_code=401, detail="Refresh token not found or already used")

        # Revoke the used token immediately - one-time use (token rotation).
        self.refresh_token_repo.delete_by_hash(token_hash)

        user_id = int(payload["sub"])
        username = stored_token["username"]

        new_access_token = self.create_access_token(user_id, username)
        new_refresh_token, new_expires_at = self.create_refresh_token(user_id)

        return new_access_token, new_refresh_token, new_expires_at

    # -- Login --#
    def login(self, username: str, password: str) -> dict:
        """Verify credentials and return a token pair. Raises 401 on invalid credentials."""
        user = self.users_repo.get_by_username(username)

        if not user or not self.verify_password(password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid username or password")

        access_token = self.create_access_token(user["id"], user["username"])
        refresh_token, _ = self.create_refresh_token(user["id"])

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": self.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }
    
    def oauth_login(self, github_id: str, email: str, name: str) -> dict:
        """Find-or-create a GitHub OAuth user and return tokens."""
        username = f"github_{github_id}"
        user = self.users_repo.get_by_username(username)

        if not user:
            password_hash = self.hash_password(secrets.token_hex(32))
            user_id = self.users_repo.insert_one(username, password_hash)
            user = self.users_repo.get_by_username(username)

        access_token = self.create_access_token(user["id"], user["username"])
        refresh_token, _ = self.create_refresh_token(user["id"])

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": self.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }

    # -- Registration --#
    def register(self, username: str, password: str) -> dict:
        """Create a new user. Raises 409 if username is taken."""
        existing = self.users_repo.get_by_username(username)
        if existing:
            raise HTTPException(status_code=409, detail="Username already taken")

        password_hash = self.hash_password(password)
        user_id = self.users_repo.insert_one(username, password_hash)

        return {"id": user_id, "username": username}

    # -- Account deletion --#
    def delete_user(self, user_id: int) -> None:
        """Delete the currently authenticated user's account and all their refresh tokens."""
        self.refresh_token_repo.delete_by_user_id(user_id)
        self.users_repo.delete_by_id(user_id)

    # -- Helpers --#
    @staticmethod
    def _hash_token(raw_token: str) -> str:
        """SHA-256 hash a token for safe database storage."""
        return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
