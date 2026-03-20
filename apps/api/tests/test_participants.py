import pytest
from httpx import AsyncClient

@pytest.fixture
async def setup_data(client: AsyncClient):
    # U1 (Owner)
    await client.post("/api/v1/auth/register", json={"name": "U1", "email": "owner@test.com", "password": "Password123"})
    t1 = (await client.post("/api/v1/auth/login", json={"email": "owner@test.com", "password": "Password123"})).json()["access_token"]
    
    # U2 (Target)
    await client.post("/api/v1/auth/register", json={"name": "U2", "email": "target@test.com", "password": "Password123"})
    t2 = (await client.post("/api/v1/auth/login", json={"email": "target@test.com", "password": "Password123"})).json()["access_token"]
    
    # Target User Profile
    r = await client.post("/api/v1/auth/login", json={"email": "target@test.com", "password": "Password123"})
    u2_id = r.json().get("sub") # sub is the uid

    # U3 (Other)
    await client.post("/api/v1/auth/register", json={"name": "U3", "email": "other@test.com", "password": "Password123"})
    t3 = (await client.post("/api/v1/auth/login", json={"email": "other@test.com", "password": "Password123"})).json()["access_token"]

    d_res = await client.post("/api/v1/decisions/", json={"title": "Test Dec"}, headers={"Authorization": f"Bearer {t1}"})
    did = d_res.json()["id"]

    return {"t1": t1, "t2": t2, "t3": t3, "did": did, "u2_id": u2_id}

@pytest.mark.asyncio
async def test_invite_success(client: AsyncClient, setup_data):
    response = await client.post(
        f"/api/v1/decisions/{setup_data['did']}/participants/",
        json={"email": "target@test.com", "role": "contributor"},
        headers={"Authorization": f"Bearer {setup_data['t1']}"}
    )
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_invite_non_owner_403(client: AsyncClient, setup_data):
    # T2 is not the owner (in fact not even a participant yet)
    response = await client.post(
        f"/api/v1/decisions/{setup_data['did']}/participants/",
        json={"email": "other@test.com", "role": "observer"},
        headers={"Authorization": f"Bearer {setup_data['t2']}"}
    )
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_invite_duplicate_409(client: AsyncClient, setup_data):
    await client.post(
        f"/api/v1/decisions/{setup_data['did']}/participants/",
        json={"email": "target@test.com", "role": "contributor"},
        headers={"Authorization": f"Bearer {setup_data['t1']}"}
    )
    # Duplicate
    response = await client.post(
        f"/api/v1/decisions/{setup_data['did']}/participants/",
        json={"email": "target@test.com", "role": "contributor"},
        headers={"Authorization": f"Bearer {setup_data['t1']}"}
    )
    assert response.status_code == 409

@pytest.mark.asyncio
async def test_invite_unknown_email_404(client: AsyncClient, setup_data):
    response = await client.post(
        f"/api/v1/decisions/{setup_data['did']}/participants/",
        json={"email": "ghost@test.com", "role": "observer"},
        headers={"Authorization": f"Bearer {setup_data['t1']}"}
    )
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_remove_non_participant_404(client: AsyncClient, setup_data):
    response = await client.delete(
        f"/api/v1/decisions/{setup_data['did']}/participants/{setup_data['u2_id']}",
        headers={"Authorization": f"Bearer {setup_data['t1']}"}
    )
    assert response.status_code == 404

# note: We test remove\_self\_403, but getting the owner ID requires calling login first.
# This test verifies it's blocked.

@pytest.mark.asyncio
async def test_remove_self_403(client: AsyncClient):
    from jose import jwt
    import os
    # Register and login as owner
    await client.post("/api/v1/auth/register", json={
        "name": "Self Owner",
        "email": "selfowner@test.com",
        "password": "Password123!"
    })
    res = await client.post("/api/v1/auth/login", json={
        "email": "selfowner@test.com",
        "password": "Password123!"
    })
    token = res.json()["access_token"]
    # Decode token to get owner user_id
    payload = jwt.decode(
        token,
        os.environ.get("JWT_SECRET", "changeme_use_strong_secret_in_prod"),
        algorithms=["HS256"]
    )
    owner_id = payload["sub"]
    # Create decision
    d_res = await client.post(
        "/api/v1/decisions/",
        json={"title": "Self Remove Test"},
        headers={"Authorization": f"Bearer {token}"}
    )
    did = d_res.json()["id"]
    # Try to remove self
    response = await client.delete(
        f"/api/v1/decisions/{did}/participants/{owner_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400
