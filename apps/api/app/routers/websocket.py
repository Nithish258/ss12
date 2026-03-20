import socketio
from app.core.security import decode_token
from app.core.config import settings
import time

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=settings.CORS_ORIGIN,
    logger=False,
    engineio_logger=False
)
socket_app = socketio.ASGIApp(sio)

def get_sio():
    return sio

_chat_timestamps = {}

@sio.event
async def connect(sid, environ, auth):
    try:
        token = auth.get("token", "").replace("Bearer ", "")
        if not token:
            raise ValueError("No token")
        payload = decode_token(token)
        await sio.save_session(sid, {
            "user_id": payload.get("sub"),
            "email": payload.get("email"),
            "name": payload.get("name")
        })
    except Exception:
        return False

@sio.event
async def disconnect(sid):
    session = await sio.get_session(sid)
    print(f"[WS] disconnected: {session.get('user_id')}")

@sio.event
async def join_room(sid, data):
    decision_id = data.get("decision_id")
    if not decision_id:
        return
    session = await sio.get_session(sid)
    await sio.enter_room(sid, decision_id)
    await sio.emit(
        "participant_status_change",
        {"user_id": session.get("user_id"), "has_submitted": False},
        room=decision_id,
        skip_sid=sid
    )

@sio.event
async def chat_message(sid, data):
    from app.database import SessionLocal
    from app.models.models import Decision
    from sqlalchemy.future import select
    import uuid

    decision_id = data.get("decision_id")
    content = data.get("content", "").strip()

    if not decision_id or not content:
        return

    session = await sio.get_session(sid)
    user_id = session.get("user_id")

    # Rate Limiting
    now = time.time()
    last = _chat_timestamps.get(user_id, 0)
    if now - last < 1.0:
        return
    _chat_timestamps[user_id] = now

    async with SessionLocal() as db:
        try:
            result = await db.execute(
                select(Decision).filter(Decision.id == uuid.UUID(decision_id))
            )
            decision = result.scalars().first()
            if not decision or decision.status != "DISCUSSION":
                await sio.emit(
                    "error",
                    {"message": "Chat only allowed during DISCUSSION state"},
                    to=sid
                )
                return
        except Exception:
            return

    await sio.emit(
        "chat_message",
        {
            "user_id": user_id,
            "name": session.get("name"),
            "content": content,
            "decision_id": decision_id
        },
        room=decision_id
    )
