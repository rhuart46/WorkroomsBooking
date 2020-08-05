"""
Create the main API and aggregate all endpoint namespaces in it.
"""
from flask_restx import Api

from .bookings import api as booking_ns
from .rooms import api as rooms_ns


api = Api(
    title="Workrooms Booking",
    version="1.0",
    description="A collection of services allowing all users to book workrooms with mutual consideration."
)
api.add_namespace(booking_ns)
api.add_namespace(rooms_ns)
