import os
from typing import Optional, Tuple

import sqlite3

from configs import config


_DB_FILE_NAME = config.DATABASE_URI.replace("sqlite:///", "")


def _connect_to_sqlite_db_file() -> Optional[Tuple[sqlite3.Connection, sqlite3.Cursor]]:
    """Connect to the expected DB file name."""
    conn = sqlite3.connect(_DB_FILE_NAME)
    cur = conn.cursor()
    return conn, cur


def init_sqlite_db() -> None:
    """
    Create a SQLite database, the data structures involved in the project,
    and initialize it with the constant set of rooms.
    """
    # Connect to the database:
    if _DB_FILE_NAME in os.listdir(os.getcwd()):
        return None
    conn, cur = _connect_to_sqlite_db_file()

    # Create the tables representing our data structures: the rooms and the bookings.
    # As a modelization choice, we also create a building table which defines groups of rooms,
    # allowing us to store common information like the local time zone:
    cur.execute(
        """
        CREATE TABLE buildings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            address TEXT NOT NULL,
            tz_name TEXT NOT NULL
        );
        """
    )
    cur.execute(
        """
        CREATE TABLE rooms (
            code TEXT PRIMARY KEY,
            building_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            floor INTEGER NOT NULL,
            capacity INTEGER,
            FOREIGN KEY(building_id) REFERENCES buildings(id)
        );
        """
    )
    cur.execute(
        """
        CREATE TABLE bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            author TEXT NOT NULL,
            start_datetime TEXT NOT NULL,
            duration INTEGER NOT NULL,
            room_code TEXT NOT NULL,
            FOREIGN KEY(room_code) REFERENCES rooms(code)
        );
        """
    )

    # Populate the rooms:
    cur.execute(
        """
        INSERT INTO buildings ('address', 'tz_name')
        VALUES
            ('Immeuble Basalte La Défense, 17 Cours Valmy 7, 92800 Puteaux', 'Europe/Paris');
        """
    )
    cur.execute(
        """
        INSERT INTO rooms
        VALUES 
            ('room0', 1, 'Auditorium', 0, 250),
            ('room1', 1, 'Salle Ada Lovelace', 1, 12),
            ('room2', 1, 'Salle Blaise Pascal', 1, 20),
            ('room3', 1, 'Salle Claude Shannon', 1, 18),
            ('room4', 1, 'Salle Dennis Ritchie', 2, 30),
            ('room5', 1, 'Salle Edsger Dijkstra', 2, 21),
            ('room6', 1, 'Salle Fredrik Rosin Bull', 2, 13),
            ('room7', 1, 'Salle Guido van Rossum', 3, 10),
            ('room8', 1, 'Salle Haskell Curry', 3, 15),
            ('room9', 1, 'Salle John von Neumann', 3, 40);
        """
    )

    # End the process:
    conn.commit()
    conn.close()


def empty_sqlite_db() -> None:
    """Deletes all elements of the SQLite database."""
    # Connect to the database:
    conn, cur = _connect_to_sqlite_db_file()

    # Drop all tables:
    for table_name in ("bookings", "rooms", "buildings"):
        cur.execute(f"DROP TABLE {table_name};")

    # End the process:
    conn.commit()
    conn.close()
