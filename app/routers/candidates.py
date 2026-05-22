from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app import schemas, crud
from app.database import get_db
from typing import List

router = APIRouter(prefix="/candidates", tags=["candidates"])

@router.get("/", response_model=List[schemas.CandidateResponse])
async def list_candidates(db: AsyncSession = Depends(get_db)):
    return await crud.get_candidates(db)