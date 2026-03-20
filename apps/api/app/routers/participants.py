from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.schemas import InviteParticipantRequest
from app.services.participants_service import invite_participant, remove_participant
from app.core.dependencies import get_db, get_current_user
from app.models.models import User

router = APIRouter()

@router.post("/")
async def invite(decision_id: str, dto: InviteParticipantRequest, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return await invite_participant(db, decision_id, dto, user)

@router.delete("/{user_id}")
async def remove(decision_id: str, user_id: str, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return await remove_participant(db, decision_id, user_id, user)
