import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.config import settings
from app.middleware.rate_limit import limiter
from app.routers import auth, decisions, participants

# Startup Checks
if not settings.JWT_SECRET:
    raise RuntimeError("FATAL: JWT_SECRET not set")
if not getattr(settings, "DATABASE_URL", None):
    raise RuntimeError("FATAL: DATABASE_URL not set")

app = FastAPI(title="QUAICU API", docs_url="/api/docs")

# Rate Limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.CORS_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Sub-router attach logic for participants
decisions_router = decisions.router
participants_router = participants.router

# We attach decision_id into the participants router scope by mounting it under decisions
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(decisions.router, prefix="/api/v1/decisions", tags=["decisions"])
app.include_router(participants.router, prefix="/api/v1/decisions/{decision_id}/participants", tags=["participants"])


