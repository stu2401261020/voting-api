from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, String, select, PrimaryKeyConstraint, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel
from typing import List
import os

# Define the database URL and create the SQLAlchemy engine
DATABASE_URL = os.environ.get('DATABASE_URL')

# Create a FastAPI instance
app = FastAPI()

# SQLAlchemy setup
Base = declarative_base()
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define the VoteRegistration model
class VoteRegistration(Base):
    __tablename__ = "vote_registrations"
    
    vote_registration_id = Column(String, primary_key=True, index=True)
    votes = relationship("Vote", back_populates="vote_registration")

# Define the Vote model with a composite primary key
class Vote(Base):
    __tablename__ = "votes"
    
    vote_registration_id = Column(String, ForeignKey('vote_registrations.vote_registration_id'), index=True)
    answer = Column(String)

    __table_args__ = (
        PrimaryKeyConstraint('vote_registration_id', 'answer'),
    )
    
    vote_registration = relationship("VoteRegistration", back_populates="votes")

# Pydantic models for request bodies
class VoteRegistrationWithVotesCreate(BaseModel):
    vote_registration_id: str
    votes: List[str]  # Change to a list of strings

# Dependency to get the database session
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Route to create a vote_registration and multiple votes
@app.post("/votes/", response_model=VoteRegistrationWithVotesCreate)
def create_votes(vote_registration_with_votes: VoteRegistrationWithVotesCreate, db: Session = Depends(get_db)):
    # Create the VoteRegistration
    db_vote_registration = VoteRegistration(vote_registration_id=vote_registration_with_votes.vote_registration_id)
    db.add(db_vote_registration)
    db.commit()
    db.refresh(db_vote_registration)

    # Create the Votes
    db_votes = [
        Vote(vote_registration_id=db_vote_registration.vote_registration_id, answer=answer)
        for answer in vote_registration_with_votes.votes
    ]
    db.add_all(db_votes)
    db.commit()

    return vote_registration_with_votes
