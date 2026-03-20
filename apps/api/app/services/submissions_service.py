from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from app.models.models import Decision, Participant, Submission, AuditLog, User
from app.schemas.schemas import UpsertSubmissionRequest
from app.services.state_machine import check_and_auto_lock
import uuid
from typing import List

async def upsert_submission(
    db: AsyncSession,
    decision_id: str,
    dto: UpsertSubmissionRequest,
    current_user: User,
    sio=None
) -> Submission:
    try:
        did = uuid.UUID(str(decision_id))
    except ValueError:
        raise HTTPException(status_code=404, detail="Invalid decision UUID")
        
    # Input sanitization
    raw_reasoning = dto.raw_reasoning.strip()
    if len(raw_reasoning) > 10000:
        raise HTTPException(status_code=400, detail="Submission too long (max 10000 chars)")

    # Fetch Decision
    result = await db.execute(select(Decision).filter(Decision.id == did))
    decision = result.scalars().first()
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")
        
    if decision.status != "SUBMISSION_OPEN":
        raise HTTPException(status_code=403, detail="Submissions only allowed when room is SUBMISSION_OPEN")

    # Fetch Participant
    p_res = await db.execute(
        select(Participant).filter(
            Participant.decision_id == did, 
            Participant.user_id == current_user.id
        )
    )
    participant = p_res.scalars().first()
    
    if not participant or participant.role != "contributor":
        raise HTTPException(status_code=403, detail="Only contributors can submit")

    # Check existing submission
    sub_res = await db.execute(
        select(Submission).filter(
            Submission.decision_id == did,
            Submission.user_id == current_user.id
        )
    )
    submission = sub_res.scalars().first()
    
    if submission:
        submission.raw_reasoning = raw_reasoning
        submission.confidence_score = dto.confidence_score
    else:
        submission = Submission(
            decision_id=did,
            user_id=current_user.id,
            raw_reasoning=raw_reasoning,
            confidence_score=dto.confidence_score
        )
        db.add(submission)
        
    participant.has_submitted = True
    
    audit = AuditLog(
        entity_id=did,
        actor_id=current_user.id,
        action="SUBMISSION_UPSERTED",
        metadata_json={}
    )
    db.add(audit)
    
    await db.commit()
    await db.refresh(submission)
    
    # Phase 1 extraction
    from app.workers.ai_worker import enqueue_extraction
    await enqueue_extraction(str(submission.id))

    if sio is not None:
        await sio.emit(
            "participant_status_change",
            {"user_id": str(current_user.id), "has_submitted": True},
            room=str(decision_id)
        )
        
    await check_and_auto_lock(db, decision_id, sio)
    return submission

async def get_submissions(
    db: AsyncSession,
    decision_id: str,
    current_user: User
) -> List[Submission]:
    try:
        did = uuid.UUID(str(decision_id))
    except ValueError:
        raise HTTPException(status_code=404, detail="Invalid decision UUID")
        
    # Fetch Decision
    result = await db.execute(select(Decision).filter(Decision.id == did))
    decision = result.scalars().first()
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")

    # Fetch Participant
    p_res = await db.execute(
        select(Participant).filter(
            Participant.decision_id == did, 
            Participant.user_id == current_user.id
        )
    )
    if not p_res.scalars().first():
        raise HTTPException(status_code=403, detail="Not a participant")

    STATUS_ORDER = [
        "DRAFT", "SUBMISSION_OPEN", "LOCKED_PROCESSING",
        "REVEAL_READY", "DISCUSSION", "VOTING", "CLOSED"
    ]
    
    try:
        reveal_index = STATUS_ORDER.index("REVEAL_READY")
        current_index = STATUS_ORDER.index(decision.status)
    except ValueError:
        current_index = 0
        reveal_index = 3

    sub_res = await db.execute(select(Submission).filter(Submission.decision_id == did))
    all_submissions = list(sub_res.scalars().all())

    if current_index < reveal_index:
        return [s for s in all_submissions if s.user_id == current_user.id]
    else:
        return all_submissions
