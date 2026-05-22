from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud, schemas, models
from app.database import get_db
from sqlalchemy import select
from sqlalchemy import select, func
# from sqlalchemy import select

router = APIRouter(prefix="/auth", tags=["auth"])

# # @router.post("/login", response_model=schemas.Token)
# # async def login(
# #     login_data: schemas.LoginRequest,  # using JSON body instead of form
# #     db: AsyncSession = Depends(get_db),
# # ):
# #     user = await crud.authenticate_user(db, login_data.regno, login_data.password)
# #     if not user:
# #         raise HTTPException(
# #             status_code=status.HTTP_401_UNAUTHORIZED,
# #             detail="Invalid registration number or password",
# #         )
# #     access_token_expires = timedelta(minutes=crud.ACCESS_TOKEN_EXPIRE_MINUTES)
# #     access_token = crud.create_access_token(
# #         data={"sub": str(user.id)}, expires_delta=access_token_expires
# #     )
# #     return {"access_token": access_token, "token_type": "bearer", "is_admin": user.is_staff}



# @router.post("/login", response_model=schemas.LoginResponse)
# async def login(login_data: schemas.LoginRequest, db: AsyncSession = Depends(get_db)):

#     user = await crud.authenticate_user(db, login_data.regno, login_data.password)

#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid registration number or password",
#         )

#     # check vote
#     vote_result = await db.execute(
#         select(models.Vote).where(models.Vote.user_id == user.id)
#     )
#     vote = vote_result.scalar_one_or_none()

#     access_token_expires = timedelta(minutes=crud.ACCESS_TOKEN_EXPIRE_MINUTES)

#     access_token = crud.create_access_token(
#         data={"sub": str(user.id)},
#         expires_delta=access_token_expires
#     )

#     return {
#         "access_token": access_token,
#         "token_type": "bearer",
#         "user": {
#             "regNumber": user.regno,
#             "fullName": f"{user.first_name} {user.last_name}",
#             "hasVoted": vote is not None,
#             "votedForId": vote.candidate_id if vote else None,
#             "maleVotesCount": ,
#             "femaleVoteCount" ,
#             "isAdmin": user.is_staff,
#         }
#     }


@router.post("/login", response_model=schemas.LoginResponse)
async def login(
    login_data: schemas.LoginRequest,
    db: AsyncSession = Depends(get_db)
):

    user = await crud.authenticate_user(
        db,
        login_data.regno,
        login_data.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid registration number or password",
        )
    

    result = await db.execute(
        select(
            models.Candidate.id,
            models.Candidate.gender
        )
        .join(
            models.Vote,
            models.Vote.candidate_id == models.Candidate.id
        )
        .where(
            models.Vote.user_id == user.id
        )
    )

    rows = result.all()

    male_candidate_ids = []
    female_candidate_ids = []

    for candidate_id, gender in rows:

        if gender.lower() == "male":
            male_candidate_ids.append(candidate_id)

        elif gender.lower() == "female":
            female_candidate_ids.append(candidate_id)

    male_votes_count = len(male_candidate_ids)
    female_votes_count = len(female_candidate_ids)

    access_token_expires = timedelta(
        minutes=crud.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    access_token = crud.create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "regNumber": user.regno,
            "fullName": f"{user.first_name} {user.last_name}",

            "hasVoted": (male_votes_count+female_votes_count) > 0,

            "votedCandidateIds": male_candidate_ids+female_candidate_ids,

            "maleVotesCount": male_votes_count,
            "femaleVotesCount": female_votes_count,

            # "maleCandidateIds": male_candidate_ids,
            # "femaleCandidateIds": female_candidate_ids,

            "isAdmin": user.is_staff,
        }
    }
