"""
Launch the API from the root of the project.
"""
import os
from runpy import run_path
import sys

from init_storage import init_sqlite_db


# Set the src/ directory as the root of the source code:
SRC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
sys.path.insert(0, SRC_DIR)

# Create the database if it's not present:
DB_FILE_NAME = "workrooms_booking.db"
if DB_FILE_NAME not in os.listdir(os.getcwd()):
    init_sqlite_db(DB_FILE_NAME)

# Launch the API:
run_path(os.path.join(SRC_DIR, "api.py"), run_name="workrooms_booking")
