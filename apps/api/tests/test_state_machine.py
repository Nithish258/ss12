import pytest
from httpx import AsyncClient
import pytest_asyncio
import uuid
from app.models.models import Decision, AuditLog
from sqlalchemy import select

@pytest_asyncio.fixture
async def auth_token(client: AsyncClient):
    await client.post("/api/v1/auth/register", json={"name": "Owner", "email": "sm_owner@test.com", "password": "Password123!"})
    res = await client.post("/api/v1/auth/login", json={"email": "sm_owner@test.com", "password": "Password123!"})
    return res.json()["access_token"]

@pytest.mark.asyncio
async def test_transition_draft_to_open(client: AsyncClient, auth_token: str):
    res = await client.post("/api/v1/decisions/", json={"title": "State Test"}, headers={"Authorization": f"Bearer {auth_token}"})
    did = res.json()["id"]

    trans_res = await client.post(f"/api/v1/decisions/{did}/open", headers={"Authorization": f"Bearer {auth_token}"})
    assert trans_res.status_code == 200
    assert trans_res.json()["new_state"] == "SUBMISSION_OPEN"

    # Verify via GET
    get_res = await client.get(f"/api/v1/decisions/{did}", headers={"Authorization": f"Bearer {auth_token}"})
    assert get_res.json()["status"] == "SUBMISSION_OPEN"

@pytest.mark.asyncio
async def test_invalid_transition_raises_409(client: AsyncClient, auth_token: str):
    res = await client.post("/api/v1/decisions/", json={"title": "Invalid Trans"}, headers={"Authorization": f"Bearer {auth_token}"})
    did = res.json()["id"]
    lock_res = await client.post(f"/api/v1/decisions/{did}/lock", headers={"Authorization": f"Bearer {auth_token}"})
    assert lock_res.status_code == 409

@pytest.mark.asyncio
async def test_transition_writes_audit_log(client: AsyncClient, auth_token: str, db_session):
    res = await client.post("/api/v1/decisions/", json={"title": "Audit Test"}, headers={"Authorization": f"Bearer {auth_token}"})
    did = res.json()["id"]
    await client.post(f"/api/v1/decisions/{did}/open", headers={"Authorization": f"Bearer {auth_token}"})

    # We use db_session only AFTER the client call is done to avoid locks
    await db_session.expire_all()
    audit = (await db_session.execute(select(AuditLog).filter_by(entity_id=uuid.UUID(did), action="STATE_SUBMISSION_OPEN"))).scalars().first()
    assert audit is not None
    assert audit.metadata_json.get("old_state") == "DRAFT"
    assert audit.metadata_json.get("new_state") == "SUBMISSION_OPEN"

@pytest.mark.asyncio
async def test_all_submitted_triggers_auto_lock(client: AsyncClient, auth_token: str, db_session):
    res = await client.post("/api/v1/decisions/", json={"title": "Auto Lock Test"}, headers={"Authorization": f"Bearer {auth_token}"})
    did = res.json()["id"]
    await client.post(f"/api/v1/decisions/{did}/open", headers={"Authorization": f"Bearer {auth_token}"})

    # Add contributor
    await client.post("/api/v1/auth/register", json={"name": "Contrib", "email": "contrib@test.com", "password": "Password123!"})
    c_res = await client.post("/api/v1/auth/login", json={"email": "contrib@test.com", "password": "Password123!"})
    ctoken = c_res.json()["access_token"]
    await client.post(f"/api/v1/decisions/{did}/participants", json={"email": "contrib@test.com", "role": "contributor"}, headers={"Authorization": f"Bearer {auth_token}"})

    # Submit
    sub_res = await client.post(f"/api/v1/decisions/{did}/submissions", json={"raw_reasoning": "My reason", "confidence_score": 8}, headers={"Authorization": f"Bearer {ctoken}"})
    assert sub_res.status_code == 200

    # Verify auto-lock via GET
    # We might need a small sleep if there's any async processing, but it's synchronous in our code
    get_res = await client.get(f"/api/v1/decisions/{did}", headers={"Authorization": f"Bearer {auth_token}"})
    assert get_res.json()["status"] == "LOCKED_PROCESSING"

    # Also verify AuditLog for "system" actor
    await db_session.expire_all()
    audit = (await db_session.execute(select(AuditLog).filter_by(entity_id=uuid.UUID(did), action="STATE_LOCKED_PROCESSING"))).scalars().first()
    assert audit is not None
    assert audit.actor_id is None  # "system"
