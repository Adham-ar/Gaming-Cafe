from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Float
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import ForeignKey
from datetime import datetime

engine = create_engine("sqlite:///users.db")
Base = declarative_base()
Session = sessionmaker(bind=engine)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

class Item(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True)
    label = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))

    start_time = Column(DateTime, nullable=True)
    is_running = Column(Boolean, default=False)
    is_paused = Column(Boolean, default=False)
    pause_start = Column(DateTime, nullable=True)  # NEW: When did the pause begin?


class Pricing(Base):
    __tablename__ = 'pricing'
    id = Column(Integer, primary_key=True)
    category = Column(String, unique=True)
    price_per_hour = Column(Float, default=10.0)

# Create the .db file and table
Base.metadata.create_all(engine)