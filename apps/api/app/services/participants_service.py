from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.models import Participant, Decision, User, AuditLog
from app.schemas.schemas import InviteParticipantRequest
from fastapi import HTTPException, status
import uuid

async def invite_participant(db: AsyncSession, decision_id: str, dto: InviteParticipantRequest, current_user: User):
    try:
        did = uuid.UUID(decision_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Decision not found")

    result = await db.execute(select(Decision).filter(Decision.id == did))
    decision = result.scalars().first()
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")

    owner_check = await db.execute(
        select(Participant).filter(Participant.decision_id == did, Participant.user_id == current_user.id, Participant.role == "owner")
    )
    if not owner_check.scalars().first():
        raise HTTPException(status_code=403, detail="Only owner can invite")

    user_result = await db.execute(select(User).filter(User.email == dto.email))
    target_user = user_result.scalars().first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    existing_p = await db.execute(
        select(Participant).filter(Participant.decision_id == did, Participant.user_id == target_user.id)
    )
    if existing_p.scalars().first():
        raise HTTPException(status_code=409, detail="User already a participant")

    participant = Participant(decision_id=did, user_id=target_user.id, role=dto.role)
    db.add(participant)
    
    audit = AuditLog(
        entity_id=did,
        actor_id=current_user.id,
        action="PARTICIPANT_INVITED",
        metadata_json={"target_user_id": str(target_user.id)}
    )
    db.add(audit)
    await db.commit()

    # Return updated list
    parts = await db.execute(select(Participant).filter(Participant.decision_id == did))
    return parts.scalars().all()

async def remove_participant(db: AsyncSession, decision_id: str, user_id: str, current_user: User):
    try:
        did = uuid.UUID(decision_id)
        uid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Invalid UUID")

    if uid == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot remove self")

    result = await db.execute(select(Decision).filter(Decision.id == did))
    if not result.scalars().first():
        raise HTTPException(status_code=404, detail="Decision not found")

    owner_check = await db.execute(
        select(Participant).filter(Participant.decision_id == did, Participant.user_id == current_user.id, Participant.role == "owner")
    )
    if not owner_check.scalars().first():
        raise HTTPException(status_code=403, detail="Only owner can remove")

    target_p = await db.execute(
        select(Participant).filter(Participant.decision_id == did, Participant.user_id == uid)
    )
    p_obj = target_p.scalars().first()
    if not p_obj:
        raise HTTPException(status_code=404, detail="Target not a participant")

    await db.delete(p_obj)
    
    audit = AuditLog(
        entity_id=did,
        actor_id=current_user.id,
        action="PARTICIPANT_REMOVED",
        metadata_json={"target_user_id": str(uid)}
    )
    db.add(audit)
    await db.commit()

    parts = await db.execute(select(Participant).filter(Participant.decision_id == did))
    return parts.scalars().all()
