from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app import schemas, crud
from app.database import get_db
from typing import List

router = APIRouter(prefix="/votes", tags=["votes"])

# @router.post("/", response_model=schemas.VoteResponse, status_code=status.HTTP_201_CREATED)
# async def cast_vote(vote: schemas.VoteCreate, db: AsyncSession = Depends(get_db)):
#     return await crud.cast_vote(db, vote)

# @router.get("/results", response_model=List[schemas.CandidateVoteCount])
# async def vote_results(db: AsyncSession = Depends(get_db)):
#     return await crud.get_results(db)

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app import schemas, crud
from app.database import get_db
from app.crud import get_current_user

router = APIRouter(prefix="/votes", tags=["votes"])


@router.post("/", response_model=schemas.VoteResponse, status_code=status.HTTP_201_CREATED)
async def cast_vote(
    vote: schemas.VoteCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await crud.cast_vote(db, vote.candidate_id, current_user)


@router.get("/results", response_model=List[schemas.CandidateVoteCount])
async def vote_results(db: AsyncSession = Depends(get_db)):
    return await crud.get_results(db)