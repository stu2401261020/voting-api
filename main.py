from typing import Optional

from fastapi import FastAPI
from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

app = FastAPI()

# Define the database URL and create the SQLAlchemy engine
database_url = os.environ.get('DATABASE_URL')
engine = create_engine(database_url)
# Create a session factory using the engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}

@app.get("/votes/{voter_id}")
async def get_votes(voter_id: str):
    # Create a new session
    db = SessionLocal()
    # Retrieve the user from the database using the user_id
    vote = db.query(vote_registrations).filter(vote_registrations.vote_registration_id == voter_id).first()
    # Close the session
    db.close()
    return {"vote": vote}
