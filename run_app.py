"""
Launch the API from the root of the project.
"""
import os
from runpy import run_path
import sys

from manage_storage import init_sqlite_db


def launch() -> None:
    # Set the src/ directory as the root of the source code:
    src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
    sys.path.insert(0, src_dir)

    # Create the database if it's not present:
    init_sqlite_db()

    # Launch the API:
    run_path(os.path.join(src_dir, "app.py"), run_name="workrooms_booking")


if __name__ == "__main__":
    launch()
