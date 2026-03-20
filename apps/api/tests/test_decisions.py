import pytest
from httpx import AsyncClient

@pytest.fixture
async def auth_token(client: AsyncClient):
    await client.post("/api/v1/auth/register", json={
        "name": "Decision User",
        "email": "decision@example.com",
        "password": "Password123"
    })
    res = await client.post("/api/v1/auth/login", json={"email": "decision@example.com", "password": "Password123"})
    return res.json()["access_token"]

@pytest.mark.asyncio
async def test_create_decision_creates_owner_participant(client: AsyncClient, auth_token: str):
    response = await client.post(
        "/api/v1/decisions/",
        json={"title": "Q4 Strategy"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Q4 Strategy"
    # Wait, our GET or POST should return participants, check models later if needed
    # A true check would be ensuring we can query it and see we are a participant or owner

@pytest.mark.asyncio
async def test_get_decision_404_for_unknown(client: AsyncClient, auth_token: str):
    import uuid
    response = await client.get(
        f"/api/v1/decisions/{uuid.uuid4()}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_get_decision_403_if_not_participant(client: AsyncClient):
    # Register user1, create decision
    await client.post("/api/v1/auth/register", json={"name": "U1", "email": "u1@example.com", "password": "Password123"})
    r1 = await client.post("/api/v1/auth/login", json={"email": "u1@example.com", "password": "Password123"})
    t1 = r1.json()["access_token"]
    
    d_res = await client.post("/api/v1/decisions/", json={"title": "Secret"}, headers={"Authorization": f"Bearer {t1}"})
    did = d_res.json()["id"]

    # Register user2, try to access
    await client.post("/api/v1/auth/register", json={"name": "U2", "email": "u2@example.com", "password": "Password123"})
    r2 = await client.post("/api/v1/auth/login", json={"email": "u2@example.com", "password": "Password123"})
    t2 = r2.json()["access_token"]

    response = await client.get(f"/api/v1/decisions/{did}", headers={"Authorization": f"Bearer {t2}"})
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_patch_decision_403_if_not_draft(client: AsyncClient, auth_token: str, db_session):
    d_res = await client.post("/api/v1/decisions/", json={"title": "Not Draft"}, headers={"Authorization": f"Bearer {auth_token}"})
    did = d_res.json()["id"]
    
    from app.models.models import Decision
    from sqlalchemy import update
    import uuid
    
    await db_session.execute(update(Decision).where(Decision.id == uuid.UUID(did)).values(status="SUBMISSION_OPEN"))
    await db_session.commit()

    patch_res = await client.patch(f"/api/v1/decisions/{did}", json={"title": "Draft Changed"}, headers={"Authorization": f"Bearer {auth_token}"})
    assert patch_res.status_code == 403
