from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Float
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
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
    console_type = Column(String, default="PS 4")
    player_mode = Column(String, default="Single")


class Pricing(Base):
    __tablename__ = 'pricing'
    id = Column(Integer, primary_key=True)
    category = Column(String, unique=True)
    price_per_hour = Column(Float, default=00.0)

class Drinks(Base):
    __tablename__ = 'drinks'
    id = Column(Integer, primary_key=True)
    name = Column(Integer, nullable=False, unique=True)
    price = Column(Float, nullable=False)

    orders = relationship("ConsoleOrder", back_populates="drink", cascade="all, delete-orphan")


class ConsoleOrder(Base):
    __tablename__ = 'console_orders'
    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey('items.id'), nullable=False) # Which console ordered it
    drink_id = Column(Integer, ForeignKey('drinks.id'), nullable=False) # Which drink did they buy
    quantity = Column(Integer, default=1, nullable=False)

    drink = relationship("Drinks", back_populates="orders")
    item = relationship("Item")


# Create the .db file and table
Base.metadata.create_all(engine)