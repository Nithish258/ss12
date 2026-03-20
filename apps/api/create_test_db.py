import asyncio
import asyncpg

async def create_db():
    conn = await asyncpg.connect('postgresql://postgres:postgres@localhost:5432/postgres')
    try:
        await conn.execute('CREATE DATABASE quaicu_test')
    except asyncpg.exceptions.DuplicateDatabaseError:
        pass
    await conn.close()

if __name__ == "__main__":
    asyncio.run(create_db())
