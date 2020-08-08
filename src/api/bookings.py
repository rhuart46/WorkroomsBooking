import datetime as dt
from typing import Any, Dict

from flask_restx import Namespace, Resource, fields, inputs, marshal
from flask_restx.reqparse import RequestParser
from sqlalchemy import func
from werkzeug.exceptions import NotFound, UnprocessableEntity

from lib.algorithms import get_available_slots, is_room_available
from lib.sqlalchemy.session import new_session
from lib.sqlalchemy.models import Booking, Room

from api.rooms import room_model


# Initialize the collection of endpoints related to bookings themselves, that will be populated in this file:
api = Namespace("Bookings", path="/booking", description="Endpoints to use for all operations on bookings themselves.")


# Definitions of output models:
available_period_model = api.model("single_available_period", {
    "start_datetime": fields.DateTime(
        description="Start date and hour of the meeting in ISO 8601 format. "
                    "Non-zero minutes and seconds are not supported.",
        example="2020-08-04 09:00:00",
    ),
    "duration_in_hours": fields.Integer(
        description="The number of hours for which the booking must be registered.",
        example="2",
    ),
})
room_availabilities_model = api.model("range_of_availabilities", {
    "room_code": fields.String(description="Code (identifier) of a room.", example="room0"),
    "free_slots": fields.List(
        fields.Nested(available_period_model),
        help="A range of available periods for this room."
    ),
})
booking_short_model = api.model("bookings_collection_item", {
    "id": fields.Integer(description="Automatically generated identifier (number) of the booking."),
    "author": fields.String(description="Name of the booking author."),
    "start_datetime": fields.DateTime(
        description="Start date and hour of the meeting in ISO 8601 format. "
                    "Non-zero minutes and seconds are not supported.",
        example="2020-08-04 09:00:00",
    ),
    "duration_in_hours": fields.Integer(
        description="The number of hours for which the booking must be registered.",
        example="2",
    ),
    "room_code": fields.String(description="Identifier code of the booked room.", example="room0")
})
booking_model = api.clone("single_booking", booking_short_model, {
    "room": fields.Nested(room_model, description="Full information about the booked room.")
})


# Definitions of inputs parser(s) and/or validator(s):
def _list_parser() -> RequestParser:
    parser = RequestParser()
    parser.add_argument("author", type=str, help="Filter bookings by the name of author.", location="args")
    parser.add_argument(
        "day",
        type=inputs.date_from_iso8601,
        default=lambda: dt.datetime.now().date().isoformat(),
        help="Filter the bookings planned during this day.",
        location="args",
    )
    parser.add_argument("room_code", type=str, help="Filter bookings taking place in this room.", location="args")
    return parser


def _post_parser() -> RequestParser:
    parser = RequestParser()
    parser.add_argument("author", type=str, required=True, help="The name of the person for whom the booking is made.")
    parser.add_argument(
        "start_datetime",
        type=inputs.datetime_from_iso8601,
        required=True,
        help="The datetime at which the booking must start (no minutes nor seconds are allowed)."
    )
    parser.add_argument(
        "duration_in_hours",
        type=int,
        required=True,
        help="Number of hours for which the booking will last."
    )
    parser.add_argument("room_code", type=str, required=True, help="Identifier of the room to book.")
    return parser


def _validate_booking_inputs(input_args: Dict[str, Any]) -> None:
    # Extract values (all are required, no error expected):
    room_code: str = input_args["room_code"]
    start_datetime: dt.datetime = input_args["start_datetime"]
    duration: int = input_args["duration_in_hours"]

    # Check that the room_code refers to an existing room:
    session = new_session()
    room = session.query(Room).get(room_code)
    if not room:
        raise NotFound(f"No room bearing the code {room_code}. Please provide a valid one.")

    # Check that the start datetime is an hour start:
    if start_datetime.minute != 0 or start_datetime.second != 0:
        raise UnprocessableEntity(
            "The start_datetime must not contain minutes nor seconds: one can only book rooms for entire hours."
        )

    # Check that the booking duration does not lead to the next day:
    if not 0 < duration <= 25:
        raise UnprocessableEntity(
            "No booking duration is allowed to exceed a day. "
            "The parameter duration_in_hours must be a positive number less or equal to 24."
        )


def _post_computation_parser() -> RequestParser:
    parser = RequestParser()
    parser.add_argument(
        "target_day_start",
        type=inputs.datetime_from_iso8601,
        required=True,
        help="The start datetime of the day for which we want to compute availabilities (with UTC offset).",
        default=lambda: dt.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    )
    parser.add_argument("room_code", type=str, help="Identifier of the room for which to compute availabilities.")
    parser.add_argument("floor", type=int, help="If no room_code, compute availabilities for all rooms of this floor.")
    return parser


def _validate_day_start(datetime: dt.datetime) -> None:
    if datetime.hour != 0 or datetime.minute != 0 or datetime.second != 0:
        raise UnprocessableEntity(f"This datetime does not represent a day start: {datetime}.")


#
# Endpoints:
#
@api.route("/")
class BookingsResource(Resource):
    """Actions on Booking objects not involving an existing identifier."""
    list_parser = _list_parser()

    @api.doc("list_bookings")
    @api.expect(list_parser)
    @api.marshal_list_with(booking_short_model)
    def get(self):
        """List all bookings"""
        # Get the filters from inputs:
        filters = self.list_parser.parse_args(strict=True)

        # Build the filtered query:
        query = new_session().query(Booking)
        day_filter_value = filters.pop("day")
        if day_filter_value:
            query = query.filter(func.DATE(Booking.start_datetime) == day_filter_value)
        actual_filters = {key: value for key, value in filters.items() if value is not None}
        query = query.filter_by(**actual_filters)

        # Return all matching results:
        bookings = query.all()
        return bookings, 200

    post_parser = _post_parser()

    @api.doc("post_booking")
    @api.expect(post_parser, validate=True)
    @api.response(201, "The room was successfully booked.", model=booking_model)
    @api.response(404, "Unknown room code.")
    @api.response(
        409,
        "The room is not available at this time. See the available periods returned.",
        model=room_availabilities_model,
    )
    @api.response(422, "Invalid input (start_datetime or duration).")
    def post(self):
        """Try to book a room"""
        # Get and validate inputs:
        args = self.post_parser.parse_args(strict=True)
        _validate_booking_inputs(args)

        # Check the availability of the room for the requested period:
        room_code = args["room_code"]
        start_datetime = args["start_datetime"]
        if not is_room_available(room_code, start_datetime, args["duration_in_hours"]):
            room_availability_info = get_available_slots(start_datetime, room_codes=[room_code])
            assert len(room_availability_info) == 1
            return marshal(room_availability_info[0], room_availabilities_model), 409

        # Book the room:
        new_booking = Booking(
            author=args["author"],
            start_datetime=start_datetime,
            duration=args["duration_in_hours"],
            room_code=room_code,
        )
        db_session = new_session()
        db_session.add(new_booking)
        db_session.commit()

        return marshal(new_booking, booking_model), 201


@api.route("/<int:id>")
class BookingResource(Resource):
    """Actions on a single Booking object that already exists."""

    @api.doc("get_booking")
    @api.marshal_with(booking_model)
    def get(self, id: int):
        """Get a booking from its id."""
        booking = new_session().query(Booking).get(id)
        if not booking:
            raise NotFound(f"This booking ID does not exist: {id}.")
        return booking, 200

    @api.doc("delete_booking")
    def delete(self, id: int):
        """Delete a booking identified by its id."""
        db_session = new_session()

        # First check that this booking exists:
        booking = db_session.query(Booking).get(id)
        if not booking:
            raise NotFound(f"This booking ID does not exist: {id}.")

        # Then delete it:
        db_session.delete(booking)
        db_session.commit()

        return None, 204


@api.route("/compute-availabilities")
class AvailabilitiesResource(Resource):
    """Computations of availabilities."""
    parser = _post_computation_parser()

    @api.doc("compute_availabilities")
    @api.expect(parser, validate=True)
    @api.marshal_list_with(room_availabilities_model)
    def post(self):
        """Listing all availabilities for a given day, and for a given room if requested."""
        # Get and validate inputs:
        args = self.parser.parse_args(strict=True)
        target_day_start = args["target_day_start"]
        _validate_day_start(target_day_start)
        room_code = args.get("room_code")
        floor = args.get("floor")

        # Get the rooms for which the computations must be done:
        db_session = new_session()
        if room_code:
            room = db_session.query(Room).get(room_code)
            if not room:
                raise NotFound(f"Unknown room code: {room_code}.")
            rooms = [room]
        elif floor is not None:
            rooms = db_session.query(Room).filter_by(floor=floor).all()
        else:
            rooms = db_session.query(Room).all()

        # Compute availabilities for all these rooms:
        availabilities = get_available_slots(target_day_start, room_codes=[r.code for r in rooms])
        return availabilities, 200
