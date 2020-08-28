from pytz import timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from .base import Base


class Building(Base):
    __tablename__ = "buildings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    address = Column(String, nullable=False)
    tz_name = Column(String, nullable=False)


class Room(Base):
    __tablename__ = "rooms"

    code = Column(String, primary_key=True)
    building_id = Column(Integer, ForeignKey('buildings.id'), nullable=False)
    name = Column(String, nullable=False)
    floor = Column(Integer, nullable=False)
    capacity = Column(Integer)

    building = relationship(Building, backref="rooms", lazy="joined")


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    author = Column(String, nullable=False)
    _start_datetime = Column("start_datetime", DateTime, nullable=False)
    duration = Column(Integer, nullable=False)
    room_code = Column(String, ForeignKey('rooms.code'))

    room = relationship(Room, backref="bookings", lazy="joined")

    @hybrid_property
    def start_datetime(self):
        """
        The start_datetime is assumed to have been stored in the local time zone of the room
        (SQLite loses this information).
        """
        return timezone(self.room.building.tz_name).localize(self._start_datetime)

    @start_datetime.setter
    def start_datetime(self, value):
        self._start_datetime = value

    @start_datetime.expression
    def start_datetime(self):
        """
        For now, in SQL expressions, we consider that the time zone is not really necessary...
        TODO: this is ugly, a better way may be to define a custom type "DateTimeWithTimeZone" for SQLAlchemy+SQLite,
            since it seems that SQLite in itself can handle datetimes with time zones.
        """
        return self._start_datetime
