import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/quaicu_test"

async def test_conn():
    print(f"Connecting to {DATABASE_URL}...")
    engine = create_async_engine(DATABASE_URL)
    try:
        async with engine.connect() as conn:
            print("Connection successful!")
            res = await conn.execute(text("SELECT 1"))
            print(f"Result: {res.scalar()}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(test_conn())
