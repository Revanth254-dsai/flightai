from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, func
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import ROOT

engine = create_engine(f"sqlite:///{ROOT/'flightai.db'}",
                       connect_args={"check_same_thread": False})
Session = sessionmaker(bind=engine)
Base = declarative_base()

class Price(Base):
    __tablename__ = "prices"
    city = Column(String, primary_key=True)
    price = Column(Float, nullable=False)

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True)
    city = Column(String, nullable=False)
    passenger_name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

Base.metadata.create_all(engine)