"""
Set the configuration variables for local executions.
"""


# Flask:
DEBUG = False
HOST = "localhost"
PORT = 8080


# Database:
SQLITE_FILE_NAME = "workrooms_booking.db"
DATABASE_URI = f"sqlite:///{SQLITE_FILE_NAME}"
