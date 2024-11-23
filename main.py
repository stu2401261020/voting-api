from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, String, select, PrimaryKeyConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import List, Optional
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

# Define the Vote model with a composite primary key
class Vote(Base):
    __tablename__ = "votes"
    
    vote_registration_id = Column(String, index=True)
    answer = Column(String)

    __table_args__ = (
        PrimaryKeyConstraint('vote_registration_id', 'answer'),
    )

# Pydantic models for request bodies
class VoteRegistrationCreate(BaseModel):
    vote_registration_id: str

class VoteCreate(BaseModel):
    vote_registration_id: str
    answer: str

# Dependency to get the database session
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Route to create a single vote_registration
@app.post("/vote_registrations/", response_model=VoteRegistrationCreate)
def create_vote_registration(vote_registration: VoteRegistrationCreate, db: Session = Depends(get_db)):
    db_vote_registration = VoteRegistration(vote_registration_id=vote_registration.vote_registration_id)
    db.add(db_vote_registration)
    db.commit()
    db.refresh(db_vote_registration)
    return db_vote_registration

# Route to create multiple votes
@app.post("/votes/", response_model=List[VoteCreate])
def create_votes(votes: List[VoteCreate], db: Session = Depends(get_db)):
    db_votes = [Vote(vote_registration_id=vote.vote_registration_id, answer=vote.answer) for vote in votes]
    db.add_all(db_votes)
    db.commit()
    return db_votes

# Route to get answers by vote_registration_id
@app.get("/answers/{vote_registration_id}")
def read_answers(vote_registration_id: str, db: Session = Depends(get_db)):
    result = db.execute(select(Vote.answer).where(Vote.vote_registration_id == vote_registration_id))
    answers = result.scalars().all()
    
    if not answers:
        raise HTTPException(status_code=404, detail="No answers found for this vote_registration_id")
    
    return {"answers": answers}
