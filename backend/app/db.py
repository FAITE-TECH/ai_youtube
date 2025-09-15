from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class CampaignResult(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(String, index=True)
    country = Column(String)
    audience = Column(String)
    budget_spent = Column(Float)
    predicted_watch_time = Column(Float)

class Audience(Base):
    __tablename__ = "audiences"

    id = Column(Integer, primary_key=True, index=True)
    country = Column(String)
    interests = Column(String)

def init_db():
    Base.metadata.create_all(bind=engine)
