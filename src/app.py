"""
Create and launch the application with its registered API.
"""
from flask import Flask

from api import api


# Create and configure the app:
app = Flask(__name__)
api.init_app(app)


# Run it (for local use only):
if __name__ == "workrooms_booking_local":
    from configs.local import DEBUG, HOST, PORT
    app.run(host=HOST, debug=DEBUG, port=PORT)
