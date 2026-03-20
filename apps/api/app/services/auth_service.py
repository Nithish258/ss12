from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.models import User, AuditLog
from app.schemas.schemas import RegisterRequest, LoginRequest
from app.core.security import hash_password, verify_password
from fastapi import HTTPException, status

async def register_user(db: AsyncSession, dto: RegisterRequest) -> dict:
    result = await db.execute(select(User).filter(User.email == dto.email))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    hashed_pw = hash_password(dto.password)
    user = User(name=dto.name, email=dto.email, password_hash=hashed_pw)
    db.add(user)
    await db.flush() # flush to get user.id

    audit = AuditLog(
        entity_id=user.id,
        actor_id=user.id,
        action="USER_REGISTERED",
        metadata_json={"email": user.email}
    )
    db.add(audit)
    await db.commit()
    await db.refresh(user)

    return {"sub": str(user.id), "email": user.email, "role": user.role, "name": user.name}

async def login_user(db: AsyncSession, dto: LoginRequest) -> dict:
    result = await db.execute(select(User).filter(User.email == dto.email))
    user = result.scalars().first()
    
    if not user or not verify_password(dto.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    audit = AuditLog(
        entity_id=user.id,
        actor_id=user.id,
        action="USER_LOGIN",
        metadata_json={"email": user.email}
    )
    db.add(audit)
    await db.commit()

    return {"sub": str(user.id), "email": user.email, "role": user.role, "name": user.name}
