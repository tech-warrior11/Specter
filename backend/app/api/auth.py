from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import timedelta

from app.database.database import get_db
from app.models.user import User
from app.models.audit_log import AuditLog
from app.schemas.auth import UserRegister, UserLogin, TokenResponse, UserResponse
from app.dependencies import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: UserRegister, db: AsyncSession = Depends(get_db)):
    """Registers a new user with RBAC role."""
    stmt = select(User).where((User.username == payload.username) | (User.email == payload.email))
    res = await db.execute(stmt)
    if res.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username or email already exists.")

    new_user = User(
        username=payload.username,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role=payload.role.upper()
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLogin, db: AsyncSession = Depends(get_db)):
    """Authenticates analyst credentials and returns JWT Bearer token."""
    stmt = select(User).where(User.username == payload.username)
    res = await db.execute(stmt)
    user = res.scalar_one_or_none()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password."
        )

    token = create_access_token(data={"sub": user.username, "role": user.role})

    # Record login audit event
    audit = AuditLog(actor=user.username, action="LOGIN", resource=f"user:{user.id}")
    db.add(audit)
    await db.commit()

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        role=user.role,
        username=user.username,
        expires_in_minutes=480
    )


@router.get("/me", response_model=UserResponse)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    """Retrieves current authenticated analyst profile."""
    return current_user
