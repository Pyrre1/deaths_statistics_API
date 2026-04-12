from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Request model for login endpoint"""
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password", min_length=12)

class TokenResponse(BaseModel):
    """Response model for successful login"""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Access token lifetime in seconds")


class RefreshRequest(BaseModel):
    """Request model for token refresh endpoint"""
    refresh_token: str = Field(..., description="JWT refresh token")

class RegisterRequest(BaseModel):
    """Request model for user registration endpoint"""
    username: str = Field(..., min_length=4, max_length=50,description="Username")
    password: str = Field(..., min_length=12, description="Password")

class OAuthRequest(BaseModel):
    github_id: str
    email: str
    name: str
