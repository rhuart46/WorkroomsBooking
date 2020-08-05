import datetime as dt

from flask_restx import Namespace, Resource, fields
from flask_restx.reqparse import RequestParser

from api.rooms import room_model


# Initialize the collection of endpoints related to bookings themselves, that will be populated in this file:
api = Namespace("Bookings", path="/booking", description="Endpoints to use for all operations on bookings themselves.")


# Definitions of models (can be used both for inputs and outputs):
booking_short_model = api.model("bookings_collection_item", {
    "author": fields.String(description="Name of the booking author.", required=True),
    "start_datetime": fields.DateTime(
        description="Start date and hour of the meeting in ISO 8601 format. "
                    "Non-zero minutes and seconds are not supported.",
        example="2020-08-04 09:00:00",
        required=True,
    ),
    "end_datetime": fields.DateTime(
        description="End date and hour of the meeting in ISO 8601 format. "
                    "Non-zero minutes and seconds are not supported.",
        example="2020-08-04 11:00:00",
        required=True,
    ),
    "room_code": fields.String(description="Identifier code of the booked room.", example="room0", required=True)
})
booking_model = api.clone("single_booking", booking_short_model, {
    "room": fields.Nested(room_model, description="Full information about the booked room.")
})


# Definitions of inputs parsers:
def make_post_parser() -> RequestParser:
    parser = api.parser()
    # TODO
    return parser


# Endpoints (as parts of Flask-RESTX resources):
@api.route("/")
class BookingsResource(Resource):
    post_parser = make_post_parser()

    @api.doc("list_bookings")
    @api.marshal_list_with(booking_short_model)
    def get(self):
        """List all bookings"""
        bookings = [
            {
                "author": "Mr. Foo",
                "start_datetime": dt.datetime.strptime("2020-02-02 10:00:00", "%Y-%m-%d %H:%M:%S"),
                "end_datetime": dt.datetime.strptime("2020-02-02 12:00:00", "%Y-%m-%d %H:%M:%S"),
                "room_code": "room0",
            }
        ]
        return bookings

    @api.doc("post_booking")
    @api.response(409, "The room is not available at this time.")
    @api.marshal_with(booking_model, code=201)
    def post(self):
        """Try to book a room"""
        new_booking = {
            "author": "Mr. Foo",
            "start_datetime": dt.datetime.strptime("2020-02-02 10:00:00", "%Y-%m-%d %H:%M:%S"),
            "end_datetime": dt.datetime.strptime("2020-02-02 12:00:00", "%Y-%m-%d %H:%M:%S"),
            "room_code": "room0",
        }
        return new_booking, 201
