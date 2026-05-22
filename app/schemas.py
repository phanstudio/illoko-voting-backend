from pydantic import BaseModel, ConfigDict
from enum import Enum

class Gender(str, Enum):
    male = "male"
    female = "female"

# ---------- User ----------
class UserCreate(BaseModel):
    regno: str
    first_name: str
    last_name: str
    password: str

class UserResponse(BaseModel):
    id: int
    regno: str
    first_name: str
    last_name: str
    is_staff: bool

    model_config = ConfigDict(from_attributes=True)

class UserSession(BaseModel):
    regNumber: str
    fullName: str
    hasVoted: bool
    votedCandidateIds: list[int]
    isAdmin: bool
    maleVotesCount: int
    femaleVotesCount: int

class LoginRequest(BaseModel):
    regno: str
    password: str | None = None

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserSession

# ---------- Candidate ----------
class SimpleCandidateBase(BaseModel):
    name: str
    gender: Gender

class CandidateBase(SimpleCandidateBase):
    image: str | None = None
    class_name: str

class CandidateResponse(CandidateBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# ---------- Vote ----------
class VoteCreate(BaseModel):
    candidate_id: int

class VotedCandidateResponse(SimpleCandidateBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class VoteResponse(BaseModel):
    # id: int
    candidate: VotedCandidateResponse
    user_id: int

    model_config = ConfigDict(from_attributes=True)

# Result
class CandidateVoteCount(BaseModel):
    candidate: CandidateResponse
    total_votes: int
