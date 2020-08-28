"""
Set here the configurations for all environments.
"""
import os


#
# Define the configurations:
#
class _BaseConfig:
    """Base configuration, using local database and server."""
    DEBUG = False
    TESTING = False
    SERVER_NAME = "localhost:5000"
    DATABASE_URI = "sqlite:///workrooms_booking.db"


class _TestConfig(_BaseConfig):
    """Configuration used for integration tests."""
    TESTING = True
    DATABASE_URI = "sqlite:///workrooms_booking_test.db"


#
# Select the relevant one:
#
_configs = {
    "local": _BaseConfig,
    "test": _TestConfig,
    "dev": None,  # TODO
    "prod": None,  # TODO
}
env = os.environ["ENVIRONMENT"]
if env not in _configs:
    raise ValueError(f"Unknown ENVIRONMENT to configure: {env}")
else:
    config = _configs[env]
