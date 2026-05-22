# from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint, Boolean
# from sqlalchemy.orm import relationship
# from app.database import Base

# class User(Base):
#     __tablename__ = "users"

#     id = Column(Integer, primary_key=True, index=True)
#     regno = Column(String, unique=True, index=True, nullable=False)
#     first_name = Column(String, nullable=False)
#     last_name = Column(String, nullable=False)
#     password_hash = Column(String, nullable=False)          # NEW
#     is_staff = Column(Boolean, default=False, nullable=False)  # NEW

#     # Relationship: a user can have at most one vote
#     vote = relationship("Vote", back_populates="user", uselist=False) # 4 votes

# class Candidate(Base):
#     __tablename__ = "candidates"

#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String, nullable=False)
#     image = Column(String, nullable=True)   # URL to image
#     class_name = Column("class", String, nullable=False)

#     votes = relationship("Vote", back_populates="candidate")

# class Vote(Base):
#     __tablename__ = "votes"

#     id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
#     candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)

#     user = relationship("User", back_populates="vote")
#     candidate = relationship("Candidate", back_populates="votes")

#     __table_args__ = (
#         UniqueConstraint("user_id", name="uq_votes_user_id"),   # ensures one vote per user
#     )


from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    regno = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    is_staff = Column(Boolean, default=False, nullable=False)

    votes = relationship("Vote", back_populates="user")


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    image = Column(String, nullable=True)
    class_name = Column(String, nullable=False)
    gender = Column(String, nullable=False)  # "male" | "female"

    votes = relationship("Vote", back_populates="candidate")


class Vote(Base):
    __tablename__ = "votes"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)

    user = relationship("User", back_populates="votes")
    candidate = relationship("Candidate", back_populates="votes")

    __table_args__ = (
        UniqueConstraint("user_id", "candidate_id", name="uq_user_candidate_vote"),
    )
