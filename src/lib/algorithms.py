"""
A collection of small algorithms serving business purposes.
"""
import datetime as dt
from typing import Dict, List, Tuple, TypedDict, Union

from sqlalchemy import func

from lib.sqlalchemy.session import new_session
from lib.sqlalchemy.models import Booking


def is_room_available(room_code: str, start_datetime: dt.datetime, duration_in_hours: int) -> bool:
    """
    Returns True if the room is available during the whole requested period, False otherwise.
    """
    # Get all bookings related to this room:
    db_session = new_session()
    daily_room_bookings = db_session.query(Booking) \
        .filter_by(room_code=room_code) \
        .filter(func.DATE(Booking.start_datetime) == start_datetime.date()) \
        .all()

    # Detect any booked period overlapping the requested one:
    end_datetime = start_datetime + dt.timedelta(hours=duration_in_hours)
    for booking in daily_room_bookings:
        if start_datetime < booking.start_datetime < end_datetime or \
                start_datetime < booking.start_datetime + dt.timedelta(hours=booking.duration) < end_datetime:
            return False

    # If none was found, the room is available:
    return True


class FreeSlot(TypedDict):
    start_datetime: dt.datetime
    duration_in_hours: int


class RoomFreeSlots(TypedDict):
    room_code: str
    free_slots: List[FreeSlot]


def get_available_slots(requested_day_start: dt.datetime, *, room_codes: List[str]) -> List[RoomFreeSlots]:
    """
    Return the list of bookable periods during the requested day for the target rooms.
    """
    # Get all bookings related to these rooms:
    db_session = new_session()
    requested_day_bookings = db_session.query(Booking) \
        .filter(Booking.room_code.in_(room_codes), func.DATE(Booking.start_datetime) == requested_day_start.date()) \
        .order_by(Booking.room_code, Booking.start_datetime) \
        .all()

    # Reorganize the results per room:
    bookings_per_room = {}
    for booking in requested_day_bookings:
        bookings_per_room.setdefault(booking.room_code, []).append(booking)

    # Compute the remaining free slots for each room having at least one booking:
    free_slots = []
    for code, room_bookings in bookings_per_room.items():
        room_free_slots = []

        # First, detect if there is a free slot before the first booking:
        first_booking_start: dt.datetime = room_bookings[0].start_datetime
        if first_booking_start.hour != 0:
            room_free_slots.append(
                {"start_datetime": requested_day_start, "duration_in_hours": first_booking_start.hour}
            )

        # Second, detect all available slots between two bookings:
        for i, booking in enumerate(requested_day_bookings[:-1]):
            current_booking_end_datetime = booking.start_datetime + dt.timedelta(hours=booking.duration)
            next_booking_start_datetime = requested_day_bookings[i+1].start_datetime
            if current_booking_end_datetime != next_booking_start_datetime:
                new_free_slot_timedelta = next_booking_start_datetime - current_booking_end_datetime
                new_free_slot_duration_in_hours = int(new_free_slot_timedelta.total_seconds() // 3600)
                room_free_slots.append(
                    {
                        "start_datetime": current_booking_end_datetime,
                        "duration_in_hours": new_free_slot_duration_in_hours,
                    }
                )

        # Finally, detect if there is a free slot at the end of the day, after the last booking:
        last_booking = requested_day_bookings[-1]
        last_booking_end = last_booking.start_datetime + dt.timedelta(last_booking.duration)
        if last_booking_end.hour != 0:
            room_free_slots.append({"start_datetime": last_booking_end, "duration_in_hours": 24-last_booking_end.hour})

        # Save the results:
        free_slots.append({"room_code": code, "free_slots": room_free_slots})

    # Also return the availability information the rooms that are free for the whole day (for which no booking exists):
    for code in room_codes:
        if code not in bookings_per_room:
            room_free_slots = [{"start_datetime": requested_day_start, "duration_in_hours": 24}]
            free_slots.append({"room_code": code, "free_slots": room_free_slots})

    return free_slots
