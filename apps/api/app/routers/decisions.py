from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.schemas import CreateDecisionRequest, UpdateDecisionRequest
from app.services.decisions_service import create_decision, get_decisions_for_user, get_decision_by_id, update_decision
from app.core.dependencies import get_db, get_current_user
from app.models.models import User

router = APIRouter()

@router.post("/")
async def create(dto: CreateDecisionRequest, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return await create_decision(db, dto, user)

@router.get("/")
async def list_all(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return await get_decisions_for_user(db, user)

@router.get("/{decision_id}")
async def get_one(decision_id: str, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return await get_decision_by_id(db, decision_id, user)

@router.patch("/{decision_id}")
async def update(decision_id: str, dto: UpdateDecisionRequest, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return await update_decision(db, decision_id, dto, user)
