from datetime import timedelta
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from app.core.security import create_access_token
from app.core.config import settings
from typing import Optional
from app.cache.redis_cache import cache

router = APIRouter(prefix="/auth", tags=["auth"])

class UserAuthRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, example="admin")
    password: str = Field(..., min_length=4, max_length=50, example="password")

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class MessageResponse(BaseModel):
    success: bool
    message: str

# Fallback in-memory database for local development or if Redis is offline
USERS_DB = {
    "admin": "password"
}

# Seed default admin user into Redis if available
try:
    if cache.client and not cache.client.hexists("users_db", "admin"):
        cache.client.hset("users_db", "admin", "password")
except Exception:
    pass

def get_user_password(username: str) -> Optional[str]:
    username = username.strip()
    if cache.client:
        try:
            stored_pass = cache.client.hget("users_db", username)
            if stored_pass:
                return stored_pass
        except Exception:
            pass
    return USERS_DB.get(username)

def save_user(username: str, password: str) -> bool:
    username = username.strip()
    if cache.client:
        try:
            cache.client.hset("users_db", username, password)
            return True
        except Exception:
            pass
    USERS_DB[username] = password
    return True

@router.post("/signup", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def signup(payload: UserAuthRequest):
    username = payload.username.strip()
    existing_pass = get_user_password(username)
    if existing_pass:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    save_user(username, payload.password)
    return MessageResponse(success=True, message="User registered successfully! You can now log in.")

@router.post("/login", response_model=TokenResponse)
async def login(payload: UserAuthRequest):
    username = payload.username.strip()
    stored_pass = get_user_password(username)
    if stored_pass and stored_pass == payload.password:
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        token = create_access_token(
            subject=username, expires_delta=access_token_expires
        )
        return TokenResponse(access_token=token)
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
    )
