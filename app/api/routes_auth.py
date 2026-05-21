from datetime import timedelta
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from app.core.security import create_access_token
from app.core.config import settings
from typing import Optional
from app.core.database import db_client

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

# Seed default admin user into database if not present
try:
    if not db_client.get_user_password("admin"):
        db_client.save_user("admin", "password")
except Exception:
    pass

def get_user_password(username: str) -> Optional[str]:
    return db_client.get_user_password(username)

def save_user(username: str, password: str) -> bool:
    return db_client.save_user(username, password)

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
