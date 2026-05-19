from datetime import timedelta
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from app.core.security import create_access_token
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

# In-memory user database
USERS_DB = {
    "admin": "password"
}

class UserAuthRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, example="admin")
    password: str = Field(..., min_length=4, max_length=50, example="password")

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class MessageResponse(BaseModel):
    success: bool
    message: str

@router.post("/signup", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def signup(payload: UserAuthRequest):
    username = payload.username.strip()
    if username in USERS_DB:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    USERS_DB[username] = payload.password
    return MessageResponse(success=True, message="User registered successfully! You can now log in.")

@router.post("/login", response_model=TokenResponse)
async def login(payload: UserAuthRequest):
    username = payload.username.strip()
    if username in USERS_DB and USERS_DB[username] == payload.password:
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        token = create_access_token(
            subject=username, expires_delta=access_token_expires
        )
        return TokenResponse(access_token=token)
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
    )
