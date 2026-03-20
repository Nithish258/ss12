import pytest
from httpx import AsyncClient
import pytest_asyncio

@pytest_asyncio.fixture
async def auth_token(client: AsyncClient):
    await client.post("/api/v1/auth/register", json={"name": "Owner", "email": "sub_owner@test.com", "password": "Password123!"})
    res = await client.post("/api/v1/auth/login", json={"email": "sub_owner@test.com", "password": "Password123!"})
    return res.json()["access_token"]

@pytest.mark.asyncio
async def test_upsert_submission_success(client: AsyncClient, auth_token: str):
    res = await client.post("/api/v1/decisions/", json={"title": "Sub Test"}, headers={"Authorization": f"Bearer {auth_token}"})
    did = res.json()["id"]
    await client.post(f"/api/v1/decisions/{did}/open", headers={"Authorization": f"Bearer {auth_token}"})
    
    await client.post("/api/v1/auth/register", json={"name": "C1", "email": "c1@test.com", "password": "Password123!"})
    c_res = await client.post("/api/v1/auth/login", json={"email": "c1@test.com", "password": "Password123!"})
    ctoken = c_res.json()["access_token"]
    await client.post(f"/api/v1/decisions/{did}/participants", json={"email": "c1@test.com", "role": "contributor"}, headers={"Authorization": f"Bearer {auth_token}"})

    sub_res = await client.post(f"/api/v1/decisions/{did}/submissions", json={"raw_reasoning": "Hello", "confidence_score": 7}, headers={"Authorization": f"Bearer {ctoken}"})
    assert sub_res.status_code == 200

@pytest.mark.asyncio
async def test_confidence_score_validation(client: AsyncClient, auth_token: str):
    res = await client.post("/api/v1/decisions/", json={"title": "Conf Test"}, headers={"Authorization": f"Bearer {auth_token}"})
    did = res.json()["id"]
    await client.post(f"/api/v1/decisions/{did}/open", headers={"Authorization": f"Bearer {auth_token}"})
    
    await client.post("/api/v1/auth/register", json={"name": "ConfC", "email": "confc@test.com", "password": "Password123!"})
    c_res = await client.post("/api/v1/auth/login", json={"email": "confc@test.com", "password": "Password123!"})
    ctoken = c_res.json()["access_token"]
    await client.post(f"/api/v1/decisions/{did}/participants", json={"email": "confc@test.com", "role": "contributor"}, headers={"Authorization": f"Bearer {auth_token}"})

    assert (await client.post(f"/api/v1/decisions/{did}/submissions", json={"raw_reasoning": "A", "confidence_score": 0}, headers={"Authorization": f"Bearer {ctoken}"})).status_code == 422
    assert (await client.post(f"/api/v1/decisions/{did}/submissions", json={"raw_reasoning": "A", "confidence_score": 11}, headers={"Authorization": f"Bearer {ctoken}"})).status_code == 422
    assert (await client.post(f"/api/v1/decisions/{did}/submissions", json={"raw_reasoning": "A", "confidence_score": 5}, headers={"Authorization": f"Bearer {ctoken}"})).status_code == 200

@pytest.mark.asyncio
async def test_submission_blocked_when_not_open(client: AsyncClient, auth_token: str):
    res = await client.post("/api/v1/decisions/", json={"title": "Block Sub"}, headers={"Authorization": f"Bearer {auth_token}"})
    did = res.json()["id"]
    
    await client.post("/api/v1/auth/register", json={"name": "BlockC", "email": "blockc@test.com", "password": "Password123!"})
    c_res = await client.post("/api/v1/auth/login", json={"email": "blockc@test.com", "password": "Password123!"})
    ctoken = c_res.json()["access_token"]
    await client.post(f"/api/v1/decisions/{did}/participants", json={"email": "blockc@test.com", "role": "contributor"}, headers={"Authorization": f"Bearer {auth_token}"})

    assert (await client.post(f"/api/v1/decisions/{did}/submissions", json={"raw_reasoning": "A", "confidence_score": 5}, headers={"Authorization": f"Bearer {ctoken}"})).status_code == 403

@pytest.mark.asyncio
async def test_observer_cannot_submit(client: AsyncClient, auth_token: str):
    res = await client.post("/api/v1/decisions/", json={"title": "Obs"}, headers={"Authorization": f"Bearer {auth_token}"})
    did = res.json()["id"]
    await client.post(f"/api/v1/decisions/{did}/open", headers={"Authorization": f"Bearer {auth_token}"})
    
    await client.post("/api/v1/auth/register", json={"name": "ObsC", "email": "obsc@test.com", "password": "Password123!"})
    c_res = await client.post("/api/v1/auth/login", json={"email": "obsc@test.com", "password": "Password123!"})
    ctoken = c_res.json()["access_token"]
    await client.post(f"/api/v1/decisions/{did}/participants", json={"email": "obsc@test.com", "role": "observer"}, headers={"Authorization": f"Bearer {auth_token}"})

    assert (await client.post(f"/api/v1/decisions/{did}/submissions", json={"raw_reasoning": "A", "confidence_score": 5}, headers={"Authorization": f"Bearer {ctoken}"})).status_code == 403

@pytest.mark.asyncio
async def test_submissions_hidden_before_reveal(client: AsyncClient, auth_token: str):
    res = await client.post("/api/v1/decisions/", json={"title": "Hide"}, headers={"Authorization": f"Bearer {auth_token}"})
    did = res.json()["id"]
    await client.post(f"/api/v1/decisions/{did}/open", headers={"Authorization": f"Bearer {auth_token}"})
    
    await client.post("/api/v1/auth/register", json={"name": "H1", "email": "h1@test.com", "password": "Password123!"})
    c_res = await client.post("/api/v1/auth/login", json={"email": "h1@test.com", "password": "Password123!"})
    ctoken1 = c_res.json()["access_token"]
    await client.post(f"/api/v1/decisions/{did}/participants", json={"email": "h1@test.com", "role": "contributor"}, headers={"Authorization": f"Bearer {auth_token}"})

    await client.post("/api/v1/auth/register", json={"name": "H2", "email": "h2@test.com", "password": "Password123!"})
    c_res = await client.post("/api/v1/auth/login", json={"email": "h2@test.com", "password": "Password123!"})
    ctoken2 = c_res.json()["access_token"]
    await client.post(f"/api/v1/decisions/{did}/participants", json={"email": "h2@test.com", "role": "contributor"}, headers={"Authorization": f"Bearer {auth_token}"})

    await client.post(f"/api/v1/decisions/{did}/submissions", json={"raw_reasoning": "Sub 1", "confidence_score": 5}, headers={"Authorization": f"Bearer {ctoken1}"})
    
    subs = await client.get(f"/api/v1/decisions/{did}/submissions", headers={"Authorization": f"Bearer {ctoken1}"})
    assert len(subs.json()) == 1

@pytest.mark.asyncio
async def test_submissions_visible_after_reveal(client: AsyncClient, auth_token: str, db_session):
    res = await client.post("/api/v1/decisions/", json={"title": "Reveal"}, headers={"Authorization": f"Bearer {auth_token}"})
    did = res.json()["id"]
    await client.post(f"/api/v1/decisions/{did}/open", headers={"Authorization": f"Bearer {auth_token}"})
    
    await client.post("/api/v1/auth/register", json={"name": "V1", "email": "v1@test.com", "password": "Password123!"})
    c_res = await client.post("/api/v1/auth/login", json={"email": "v1@test.com", "password": "Password123!"})
    ctoken1 = c_res.json()["access_token"]
    await client.post(f"/api/v1/decisions/{did}/participants", json={"email": "v1@test.com", "role": "contributor"}, headers={"Authorization": f"Bearer {auth_token}"})

    await client.post("/api/v1/auth/register", json={"name": "V2", "email": "v2@test.com", "password": "Password123!"})
    c_res = await client.post("/api/v1/auth/login", json={"email": "v2@test.com", "password": "Password123!"})
    ctoken2 = c_res.json()["access_token"]
    await client.post(f"/api/v1/decisions/{did}/participants", json={"email": "v2@test.com", "role": "contributor"}, headers={"Authorization": f"Bearer {auth_token}"})

    await client.post(f"/api/v1/decisions/{did}/submissions", json={"raw_reasoning": "Sub 1", "confidence_score": 5}, headers={"Authorization": f"Bearer {ctoken1}"})
    await client.post(f"/api/v1/decisions/{did}/submissions", json={"raw_reasoning": "Sub 2", "confidence_score": 5}, headers={"Authorization": f"Bearer {ctoken2}"})

    from app.models.models import Decision
    from sqlalchemy import update
    import uuid
    # Wait, if both submit, the state machine auto transitions to LOCKED_PROCESSING!
    # So we just update to REVEAL_READY
    await db_session.execute(update(Decision).where(Decision.id == uuid.UUID(did)).values(status="REVEAL_READY"))
    await db_session.commit()

    subs = await client.get(f"/api/v1/decisions/{did}/submissions", headers={"Authorization": f"Bearer {ctoken1}"})
    assert len(subs.json()) == 2
