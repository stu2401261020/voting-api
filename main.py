from typing import Optional

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, String, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os

# Define the database URL and create the SQLAlchemy engine
DATABASE_URL = os.environ.get('DATABASE_URL')

# Create a FastAPI instance
app = FastAPI()

# SQLAlchemy setup
Base = declarative_base()
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define the Votes model
class Vote(Base):
    __tablename__ = "votes"
    
    vote_registration_id = Column(String, primary_key=True, index=True)
    answer = Column(String)
# Dependency to get the database session
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Route to get answers by vote_registration_id
@app.get("/answers/{vote_registration_id}")
def read_answers(vote_registration_id: str, db: Session = Depends(get_db)):
    result = db.execute(select(Vote.answer).where(Vote.vote_registration_id == vote_registration_id))
    answers = result.scalars().all()
    
    if not answers:
        raise HTTPException(status_code=404, detail="No answers found for this vote_registration_id")
    
    return {"answers": answers}
