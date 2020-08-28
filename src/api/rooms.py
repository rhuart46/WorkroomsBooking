from flask_restx import Namespace, Resource, fields
from flask_restx.reqparse import RequestParser
from werkzeug.exceptions import NotFound

from lib.sqlalchemy.session import new_session
from lib.sqlalchemy.models import Room


# Create the namespace of endpoints related to the rooms:
api = Namespace(
    "Rooms",
    path="/rooms",
    description="Views and management of the rooms, along with all related information."
)


# Output models:
room_short_model = api.model("rooms_collection_item", {
    "code": fields.String(description="Identifier code of the room.", example="room0", required=True),
    "name": fields.String(description="Full name of the room.", example="The first room", required=True),
})
room_model = api.clone("single_room", room_short_model, {
    "floor": fields.Integer(description="The floor at which the room can be found.", example=0),
    "capacity": fields.Integer(description="The maximum number of people who can sit in the room.", example=12)
})


# Inputs parser (for filters):
def _list_parser() -> RequestParser:
    parser = RequestParser()
    parser.add_argument("search_in_name", type=str, help="Filter rooms which name contains this text.", location="args")
    parser.add_argument("floor", type=int, help="Filter rooms located at this floor of the building.", location="args")
    parser.add_argument(
        "min_capacity",
        type=int,
        help="Filter rooms in which at least this number of people can sit.",
        location="args"
    )
    return parser


@api.route("/")
class RoomsResource(Resource):
    parser = _list_parser()

    @api.doc("list_rooms")
    @api.expect(parser)
    @api.marshal_list_with(room_short_model)
    def get(self):
        """List all rooms"""
        # Get the input filters, if any:
        filters = self.parser.parse_args(strict=True)
        search_in_name = filters.get("search_in_name")
        floor = filters.get("floor")
        min_capacity = filters.get("min_capacity")

        # Build the query:
        db_session = new_session()
        query = db_session.query(Room)
        if search_in_name:
            query = query.filter(Room.name.ilike(f"%{search_in_name}%"))
        if floor is not None:
            query = query.filter_by(floor=floor)
        if min_capacity:
            query = query.filter(Room.capacity >= min_capacity)

        # Return all matching results:
        res = query.all()
        db_session.close()
        return res, 200


@api.route("/<string:code>")
class RoomResource(Resource):

    @api.doc("get_room")
    @api.marshal_with(room_model)
    def get(self, code: str):
        """Get the room identified by the code."""
        db_session = new_session()
        room = db_session.query(Room).get(code)
        db_session.close()
        if not room:
            raise NotFound(f"The code {code} does not identify any room.")
        return room, 200
