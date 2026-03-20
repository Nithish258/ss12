import os
from arq import create_pool
from arq.connections import RedisSettings

def get_redis_settings() -> RedisSettings:
    url = os.getenv("REDIS_URL", "redis://localhost:6379")
    return RedisSettings.from_dsn(url)

async def extract_arguments(ctx, submission_id: str):
    """
    Phase 1: Extract arguments from one submission.
    TODO Sprint 3: Call Gemini API here.
    """
    print(f"[STUB] extract_arguments called for submission {submission_id}")
    return {"status": "stub", "submission_id": submission_id}

async def synthesize_all(ctx, decision_id: str):
    """
    Phase 2: Cross-analyse all extracted arguments for a decision.
    TODO Sprint 3: Call Gemini API here.
    """
    print(f"[STUB] synthesize_all called for decision {decision_id}")
    return {"status": "stub", "decision_id": decision_id}

class WorkerSettings:
    functions = [extract_arguments, synthesize_all]
    redis_settings = get_redis_settings()

async def enqueue_extraction(submission_id: str):
    pool = await create_pool(get_redis_settings())
    await pool.enqueue_job("extract_arguments", submission_id)
    await pool.aclose()

async def enqueue_synthesis(decision_id: str):
    pool = await create_pool(get_redis_settings())
    await pool.enqueue_job("synthesize_all", decision_id)
    await pool.aclose()
