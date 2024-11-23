from typing import Optional

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from sqlalchemy import Column, String
import os

# Define the database URL and create the SQLAlchemy engine
DATABASE_URL = os.environ.get('DATABASE_URL')

# Create a FastAPI instance
app = FastAPI()

# SQLAlchemy setup
Base = declarative_base()
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Define the Votes model
class Vote(Base):
    __tablename__ = "votes"
    
    vote_registration_id = Column(String, primary_key=True, index=True)
    answer = Column(String)

# Dependency to get the database session
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

# Route to get answers by vote_registration_id
@app.get("/answers/{vote_registration_id}")
async def read_answers(vote_registration_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Vote.answer).where(Vote.vote_registration_id == vote_registration_id))
    answers = result.scalars().all()
    
    if not answers:
        raise HTTPException(status_code=404, detail="No answers found for this vote_registration_id")
    
    return {"answers": answers}
