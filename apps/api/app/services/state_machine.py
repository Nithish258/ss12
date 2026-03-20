from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from app.models.models import Decision, Participant, AuditLog
import uuid

VALID_TRANSITIONS = {
    "DRAFT":              "SUBMISSION_OPEN",
    "SUBMISSION_OPEN":    "LOCKED_PROCESSING",
    "LOCKED_PROCESSING":  "REVEAL_READY",
    "REVEAL_READY":       "DISCUSSION",
    "DISCUSSION":         "VOTING",
    "VOTING":             "CLOSED",
}

async def verify_owner(db: AsyncSession, decision_id: str, user_id: str):
    try:
        did = uuid.UUID(str(decision_id))
        uid = uuid.UUID(str(user_id))
    except ValueError:
        raise HTTPException(status_code=404, detail="Invalid UUID")
        
    result = await db.execute(
        select(Participant).filter(
            Participant.decision_id == did,
            Participant.user_id == uid,
            Participant.role == "owner"
        )
    )
    if not result.scalars().first():
        raise HTTPException(status_code=403, detail="Only the decision owner can change state")

async def transition_state(
    db: AsyncSession,
    decision_id: str,
    target_status: str,
    actor_id: str,
    sio=None
) -> Decision:
    try:
        did = uuid.UUID(str(decision_id))
    except ValueError:
        raise HTTPException(status_code=404, detail="Invalid decision_id format")

    result = await db.execute(select(Decision).filter(Decision.id == did))
    decision = result.scalars().first()
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")

    current_status = decision.status
    if VALID_TRANSITIONS.get(current_status) != target_status:
        raise HTTPException(
            status_code=409, 
            detail=f"Cannot transition from {current_status} to {target_status}"
        )

    decision.status = target_status
    
    # Audit logic
    try:
        act_id = uuid.UUID(str(actor_id)) if actor_id != "system" else None
    except ValueError:
        act_id = None
        
    audit = AuditLog(
        entity_id=decision.id,
        actor_id=act_id,
        action=f"STATE_{target_status}",
        metadata_json={"old_state": current_status, "new_state": target_status}
    )
    db.add(audit)
    await db.commit()

    if sio is not None:
        await sio.emit(
            "state_transition",
            {"old_state": current_status, "new_state": target_status},
            room=str(decision_id)
        )
    return decision

async def check_and_auto_lock(
    db: AsyncSession,
    decision_id: str,
    sio=None
) -> bool:
    try:
        did = uuid.UUID(str(decision_id))
    except ValueError:
        return False

    result = await db.execute(select(Decision).filter(Decision.id == did))
    decision = result.scalars().first()
    
    if not decision or decision.status != "SUBMISSION_OPEN":
        return False

    parts_res = await db.execute(
        select(Participant).filter(
            Participant.decision_id == did,
            Participant.role == "contributor"
        )
    )
    contributors = parts_res.scalars().all()
    
    if not contributors:
        return False
        
    all_submitted = all(p.has_submitted for p in contributors)
    
    if all_submitted:
        await transition_state(db, decision_id, "LOCKED_PROCESSING", "system", sio)
        
        # Enqueue AI Jobs
        from app.workers.ai_worker import enqueue_synthesis, enqueue_extraction
        # Actually enqueue extraction happens per submission, 
        # enqueue synthesis happens when locked.
        await enqueue_synthesis(str(decision_id))
        return True
        
    return False
