from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .base import Base


class Room(Base):
    __tablename__ = "rooms"

    code = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    floor = Column(Integer, nullable=False)
    capacity = Column(Integer)


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    author = Column(String, nullable=False)
    start_datetime = Column(DateTime, nullable=False)
    duration = Column(Integer, nullable=False)
    room_code = Column(String, ForeignKey('rooms.code'))

    room = relationship(Room, backref="bookings", lazy="joined")
