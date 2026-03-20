from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from app.core.dependencies import get_db, get_current_user
from app.models.models import User
from app.schemas.schemas import UpsertSubmissionRequest, SubmissionResponse, StateTransitionResponse
from app.services.submissions_service import upsert_submission, get_submissions
from app.services.state_machine import transition_state, verify_owner
from app.routers.websocket import get_sio

router = APIRouter()

def get_socket(request: Request):
    return get_sio()

@router.post("/{decision_id}/submissions", response_model=SubmissionResponse)
async def create_submission(
    decision_id: str,
    dto: UpsertSubmissionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    sio = Depends(get_socket)
):
    sub = await upsert_submission(db, decision_id, dto, current_user, sio)
    return sub

@router.get("/{decision_id}/submissions", response_model=List[SubmissionResponse])
async def list_submissions(
    decision_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    subs = await get_submissions(db, decision_id, current_user)
    return subs

@router.post("/{decision_id}/open", response_model=StateTransitionResponse)
async def state_open(decision_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user), sio = Depends(get_socket)):
    await verify_owner(db, decision_id, current_user.id)
    # Fetch current state for response metadata
    from app.models.models import Decision
    import uuid
    res = await db.execute(select(Decision).filter(Decision.id == uuid.UUID(decision_id)))
    d_obj = res.scalars().first()
    old_status = d_obj.status if d_obj else "UNKNOWN"
    
    d = await transition_state(db, decision_id, "SUBMISSION_OPEN", str(current_user.id), sio)
    return StateTransitionResponse(decision_id=str(d.id), old_state=old_status, new_state="SUBMISSION_OPEN")

@router.post("/{decision_id}/lock", response_model=StateTransitionResponse)
async def state_lock(decision_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user), sio = Depends(get_socket)):
    await verify_owner(db, decision_id, current_user.id)
    from app.models.models import Decision
    import uuid
    res = await db.execute(select(Decision).filter(Decision.id == uuid.UUID(decision_id)))
    d_obj = res.scalars().first()
    old_status = d_obj.status if d_obj else "UNKNOWN"

    d = await transition_state(db, decision_id, "LOCKED_PROCESSING", str(current_user.id), sio)
    return StateTransitionResponse(decision_id=str(d.id), old_state=old_status, new_state="LOCKED_PROCESSING")

@router.post("/{decision_id}/reveal", response_model=StateTransitionResponse)
async def state_reveal(decision_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user), sio = Depends(get_socket)):
    await verify_owner(db, decision_id, current_user.id)
    from app.models.models import Decision
    import uuid
    res = await db.execute(select(Decision).filter(Decision.id == uuid.UUID(decision_id)))
    d_obj = res.scalars().first()
    old_status = d_obj.status if d_obj else "UNKNOWN"

    d = await transition_state(db, decision_id, "REVEAL_READY", str(current_user.id), sio)
    return StateTransitionResponse(decision_id=str(d.id), old_state=old_status, new_state="REVEAL_READY")

@router.post("/{decision_id}/discuss", response_model=StateTransitionResponse)
async def state_discuss(decision_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user), sio = Depends(get_socket)):
    await verify_owner(db, decision_id, current_user.id)
    from app.models.models import Decision
    import uuid
    res = await db.execute(select(Decision).filter(Decision.id == uuid.UUID(decision_id)))
    d_obj = res.scalars().first()
    old_status = d_obj.status if d_obj else "UNKNOWN"

    d = await transition_state(db, decision_id, "DISCUSSION", str(current_user.id), sio)
    return StateTransitionResponse(decision_id=str(d.id), old_state=old_status, new_state="DISCUSSION")

@router.post("/{decision_id}/vote", response_model=StateTransitionResponse)
async def state_vote(decision_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user), sio = Depends(get_socket)):
    await verify_owner(db, decision_id, current_user.id)
    from app.models.models import Decision
    import uuid
    res = await db.execute(select(Decision).filter(Decision.id == uuid.UUID(decision_id)))
    d_obj = res.scalars().first()
    old_status = d_obj.status if d_obj else "UNKNOWN"

    d = await transition_state(db, decision_id, "VOTING", str(current_user.id), sio)
    return StateTransitionResponse(decision_id=str(d.id), old_state=old_status, new_state="VOTING")

@router.post("/{decision_id}/close", response_model=StateTransitionResponse)
async def state_close(decision_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user), sio = Depends(get_socket)):
    await verify_owner(db, decision_id, current_user.id)
    from app.models.models import Decision
    import uuid
    res = await db.execute(select(Decision).filter(Decision.id == uuid.UUID(decision_id)))
    d_obj = res.scalars().first()
    old_status = d_obj.status if d_obj else "UNKNOWN"

    d = await transition_state(db, decision_id, "CLOSED", str(current_user.id), sio)
    return StateTransitionResponse(decision_id=str(d.id), old_state=old_status, new_state="CLOSED")
