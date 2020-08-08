"""
Launch the API from the root of the project.
"""
import os
from runpy import run_path
import sys

from configs.local import SQLITE_FILE_NAME

from init_storage import init_sqlite_db


# Set the src/ directory as the root of the source code:
SRC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
sys.path.insert(0, SRC_DIR)

# Create the database if it's not present:
if SQLITE_FILE_NAME not in os.listdir(os.getcwd()):
    init_sqlite_db(SQLITE_FILE_NAME)

# Launch the API:
run_path(os.path.join(SRC_DIR, "app.py"), run_name="workrooms_booking_local")
