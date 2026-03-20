import asyncio
import asyncpg

async def wipe():
    conn = await asyncpg.connect('postgresql://postgres:postgres@localhost:5432/quaicu')
    await conn.execute('DROP SCHEMA public CASCADE; CREATE SCHEMA public; GRANT ALL ON SCHEMA public TO postgres; GRANT ALL ON SCHEMA public TO public;')
    await conn.close()

if __name__ == "__main__":
    asyncio.run(wipe())
