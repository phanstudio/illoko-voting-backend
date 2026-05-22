from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app import models, schemas
from app.database import get_db
import os
from sqlalchemy.orm import selectinload

# ------- Security setup -------
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")   # login endpoint

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "fallback-secret")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# ---------- Dependency: get current user from token ----------
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = int(payload.get("sub"))
    except (JWTError, ValueError):
        raise credentials_exception
    user = await db.get(models.User, user_id)
    if user is None:
        raise credentials_exception
    return user

# ---------- Dependency: require admin ----------
async def get_current_admin_user(current_user: models.User = Depends(get_current_user)) -> models.User:
    if not current_user.is_staff:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user

# ---------- CRUD functions (updated) ----------
async def create_user(db: AsyncSession, user: schemas.UserCreate):
    # Check duplicate
    existing = await db.execute(select(models.User).where(models.User.regno == user.regno))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Registration number already registered")
    db_user = models.User(
        regno=user.regno,
        password_hash=hash_password(user.password),
        is_staff=False,  # default, only an admin can promote later
        first_name=user.first_name,
        last_name=user.last_name,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def authenticate_user(db: AsyncSession, regno: str, password: str) -> models.User | None:
    result = await db.execute(select(models.User).where(models.User.regno == regno))
    user = result.scalar_one_or_none()
    if not user or (user.is_staff and not verify_password(password, user.password_hash) ):
        return None
    return user

# Candidate CRUD remains the same (get_candidates)
# Vote CRUD will be modified to use the authenticated user

async def cast_vote(db: AsyncSession, candidate_id: int, current_user: models.User):

    # 1. get candidate
    candidate = await db.get(models.Candidate, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    # 2. enforce rule: max 2 per gender
    result = await db.execute(
        select(func.count(models.Vote.id))
        .join(models.Candidate)
        .where(
            models.Vote.user_id == current_user.id,
            models.Candidate.gender == candidate.gender
        )
    )
    count = result.scalar()

    if count >= 2:
        raise HTTPException(
            status_code=400,
            detail=f"You can only vote for 2 {candidate.gender} candidates"
        )

    # 3. prevent duplicate candidate vote
    existing = await db.execute(
        select(models.Vote).where(
            models.Vote.user_id == current_user.id,
            models.Vote.candidate_id == candidate_id
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Already voted for this candidate")

    # 4. create vote
    vote = models.Vote(
        user_id=current_user.id,
        candidate_id=candidate_id
    )

    db.add(vote)
    await db.commit()
    # await db.refresh(vote)
    vote.candidate = candidate
    return vote

# ---------- Results ----------
async def get_results(db: AsyncSession):
    # Count votes per candidate
    stmt = (
        select(models.Candidate, func.count(models.Vote.id).label("total_votes"))
        .outerjoin(models.Vote, models.Vote.candidate_id == models.Candidate.id)
        .group_by(models.Candidate.id)
    )
    result = await db.execute(stmt)
    rows = result.all()
    results = []
    for candidate, count in rows:
        results.append({
            "candidate": candidate,
            "total_votes": count,
        })
    return results

# ---------- Candidate ----------
async def get_candidates(db: AsyncSession):
    result = await db.execute(select(models.Candidate))
    return result.scalars().all()
