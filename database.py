import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()  # load .env variables

DATABASE_URL = os.getenv("DATABASE_URL")
# PostgreSQL connection string

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in your .env file")
    # stop app if DB URL missing

engine = create_engine(DATABASE_URL)
# creates DB connection engine

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)
# creates database sessions

Base = declarative_base()
# base class for all models