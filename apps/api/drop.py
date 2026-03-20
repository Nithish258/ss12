import asyncio
import os
import sys

from app.database import engine, Base
from app.models.models import User, Decision, Participant, Submission, ExtractedArgument, AiSynthesis, AuditLog

async def drop():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(drop())
