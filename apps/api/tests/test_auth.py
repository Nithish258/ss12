import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    response = await client.post("/api/v1/auth/register", json={
        "name": "Test User",
        "email": "auth@example.com",
        "password": "Password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    # Register once
    await client.post("/api/v1/auth/register", json={
        "name": "Test User",
        "email": "dup@example.com",
        "password": "Password123"
    })
    # Register again
    response = await client.post("/api/v1/auth/register", json={
        "name": "Diff User",
        "email": "dup@example.com",
        "password": "Password123"
    })
    assert response.status_code == 409

@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    await client.post("/api/v1/auth/register", json={
        "name": "Login User",
        "email": "login@example.com",
        "password": "Password123"
    })
    response = await client.post("/api/v1/auth/login", json={
        "email": "login@example.com",
        "password": "Password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data

@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    await client.post("/api/v1/auth/register", json={
        "name": "Login User",
        "email": "wrongpw@example.com",
        "password": "Password123"
    })
    response = await client.post("/api/v1/auth/login", json={
        "email": "wrongpw@example.com",
        "password": "WrongPassword123"
    })
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_login_unknown_email(client: AsyncClient):
    response = await client.post("/api/v1/auth/login", json={
        "email": "unknown@example.com",
        "password": "Password123"
    })
    assert response.status_code == 401
