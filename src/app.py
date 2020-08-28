"""
Create and launch the application with its registered API.
"""
from flask import Flask

from configs import config

from api import api


# Create and configure the app:
def create_app() -> Flask:
    _app = Flask(__name__)
    _app.config.from_object(config)
    api.init_app(_app)
    return _app


# Run it (for local use only):
if __name__ == "workrooms_booking":
    app = create_app()
    app.run()
