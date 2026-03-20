from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.schemas import RegisterRequest, LoginRequest, TokenResponse
from app.services.auth_service import register_user, login_user
from app.core.dependencies import get_db
from app.core.security import create_access_token
from app.middleware.rate_limit import limiter

router = APIRouter()

@router.post("/register", response_model=TokenResponse)
@limiter.limit("5/minute")
async def register(request: Request, dto: RegisterRequest, db: AsyncSession = Depends(get_db)):
    payload = await register_user(db, dto)
    token = create_access_token(payload)
    return TokenResponse(access_token=token)

@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
async def login(request: Request, dto: LoginRequest, db: AsyncSession = Depends(get_db)):
    payload = await login_user(db, dto)
    token = create_access_token(payload)
    return TokenResponse(access_token=token)
