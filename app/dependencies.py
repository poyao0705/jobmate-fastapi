from sqlalchemy.orm import Session
# This is the shared dependency script, such as database connection
from app.db.database import SessionLocal

def get_db():
    """Get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()