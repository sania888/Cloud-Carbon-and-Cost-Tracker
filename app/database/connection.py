from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql://postgres:1234@localhost:5432/carbon_tracker"

# Create engine
engine = create_engine(DATABASE_URL)

# Create session
SessionsLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    db = SessionsLocal()
    try:
        yield db
    finally:
        db.close()