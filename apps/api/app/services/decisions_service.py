from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.models import Decision, Participant, AuditLog, User
from app.schemas.schemas import CreateDecisionRequest, UpdateDecisionRequest
from fastapi import HTTPException, status
import uuid

async def create_decision(db: AsyncSession, dto: CreateDecisionRequest, current_user: User):
    decision = Decision(
        creator_id=current_user.id,
        title=dto.title,
        context_prompt=dto.context_prompt,
        deadline=dto.deadline
    )
    db.add(decision)
    await db.flush()

    participant = Participant(
        decision_id=decision.id,
        user_id=current_user.id,
        role="owner"
    )
    db.add(participant)
    
    audit = AuditLog(
        entity_id=decision.id,
        actor_id=current_user.id,
        action="DECISION_CREATED",
        metadata_json={"title": dto.title}
    )
    db.add(audit)
    await db.commit()
    await db.refresh(decision)
    
    # Reload with participants
    result = await db.execute(
        select(Decision).options(selectinload(Decision.participants)).filter(Decision.id == decision.id)
    )
    return result.scalars().first()

from sqlalchemy import func

async def get_decisions_for_user(db: AsyncSession, current_user: User):
    user_decisions_stmt = select(Participant.decision_id).filter(Participant.user_id == current_user.id)
    result = await db.execute(user_decisions_stmt)
    decision_ids = [r[0] for r in result.fetchall()]
    
    if not decision_ids:
        return []

    stmt = (
        select(Decision, func.count(Participant.user_id))
        .join(Participant, Decision.id == Participant.decision_id)
        .filter(Decision.id.in_(decision_ids))
        .group_by(Decision.id)
    )
    
    result = await db.execute(stmt)
    
    out = []
    for d, count in result.all():
        out.append({"id": str(d.id), "title": d.title, "status": d.status, "participant_count": count})
    return out

async def get_decision_by_id(db: AsyncSession, decision_id: str, current_user: User):
    try:
        did = uuid.UUID(decision_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Decision not found")

    result = await db.execute(
        select(Decision).options(selectinload(Decision.participants)).filter(Decision.id == did)
    )
    decision = result.scalars().first()
    
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")
        
    is_participant = any(p.user_id == current_user.id for p in decision.participants)
    if not is_participant:
        raise HTTPException(status_code=403, detail="Not a participant")
        
    return decision

async def update_decision(db: AsyncSession, decision_id: str, dto: UpdateDecisionRequest, current_user: User):
    decision = await get_decision_by_id(db, decision_id, current_user)
    
    owner_p = next((p for p in decision.participants if p.user_id == current_user.id and p.role == "owner"), None)
    if not owner_p:
        raise HTTPException(status_code=403, detail="Only owner can update")
        
    if decision.status != "DRAFT":
        raise HTTPException(status_code=403, detail="Can only update DRAFT decisions")

    if dto.title is not None:
        decision.title = dto.title
    if dto.context_prompt is not None:
        decision.context_prompt = dto.context_prompt
    if dto.deadline is not None:
        decision.deadline = dto.deadline

    updated_fields = [k for k in dto.model_dump(exclude_unset=True).keys()]
    
    audit = AuditLog(
        entity_id=decision.id,
        actor_id=current_user.id,
        action="DECISION_UPDATED",
        metadata_json={"updated_fields": updated_fields}
    )
    db.add(audit)
    await db.commit()
    await db.refresh(decision)
    return decision
