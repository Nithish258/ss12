import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
import os
os.environ["JWT_SECRET"] = "test_secret"
os.environ["DATABASE_URL"] = "postgresql+asyncpg://postgres:postgres@localhost:5432/quaicu_test"
TEST_DATABASE_URL = os.environ["DATABASE_URL"]

from app.main import app
from app.database import Base
from app.core.dependencies import get_db
from sqlalchemy import pool

import random

class TestClient(AsyncClient):
    async def request(self, method, url, **kwargs):
        headers = kwargs.get("headers") or {}
        headers["X-Forwarded-For"] = f"10.0.0.{random.randint(1, 250)}"
        kwargs["headers"] = headers
        return await super().request(method, url, **kwargs)

engine = create_async_engine(TEST_DATABASE_URL, echo=True, poolclass=pool.NullPool)
TestingSessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)

async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_db():
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)
    yield
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def db_session():
    async with TestingSessionLocal() as session:
        yield session
        # Rollback at the end of each test for isolation
        await session.rollback()

@pytest_asyncio.fixture
async def client():
    async with TestClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
