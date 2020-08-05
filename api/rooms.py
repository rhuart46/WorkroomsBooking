from flask_restx import Namespace, Resource, fields


api = Namespace(
    "Rooms",
    path="/rooms",
    description="Views and management of the rooms, along with all related information."
)


room_short_model = api.model("rooms_collection_item", {
    "code": fields.String(description="Identifier code of the room.", example="room0", required=True),
    "name": fields.String(description="Full name of the room.", example="The first room", required=True),
})
room_model = api.clone("single_room", room_short_model, {
    "floor": fields.Integer(description="The floor at which the room can be found.", example=0),
    "capacity": fields.Integer(description="The maximum number of people who can sit in the room.", example=12)
})


@api.route("/")
class Rooms(Resource):

    @api.doc("list_rooms")
    @api.marshal_list_with(room_short_model)
    def get(self):
        """List all rooms"""
        rooms = [
            {"code": "room0", "name": "Salle Ada Lovelace", "toto": "tata"},
            {"code": "room1", "name": "Salle Benjamin Franklin", "foo": "bar"},
        ]
        return rooms
