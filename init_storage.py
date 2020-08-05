import sqlite3


def init_sqlite_db(db_file_name: str) -> None:
    """
    Create a SQLite database, the data structures involved in the project,
    and initialize it with the constant set of rooms.
    """
    # Create the database:
    conn = sqlite3.connect(db_file_name)
    cur = conn.cursor()

    # Create the tables representing our data structures: the rooms and the bookings
    cur.execute(
        """
        CREATE TABLE rooms (
            code TEXT,
            name TEXT,
            floor INTEGER,
            capacity INTEGER
        );
        """
    )
    cur.execute(
        """
        CREATE TABLE bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            author TEXT,
            start_datetime TEXT,
            end_datetime TEXT,
            room_code TEXT,
            FOREIGN KEY(room_code) REFERENCES rooms(code)
        );
        """
    )

    # Populate the rooms:
    cur.execute(
        """
        INSERT INTO rooms
        VALUES 
            ('room0', 'Auditorium', 0, 250),
            ('room1', 'Salle Ada Lovelace', 1, 12),
            ('room2', 'Salle Blaise Pascal', 1, 20),
            ('room3', 'Salle Claude Shannon', 1, 18),
            ('room4', 'Salle Dennis Ritchie', 2, 30),
            ('room5', 'Salle Edsger Dijkstra', 2, 21),
            ('room6', 'Salle Fredrik Rosin Bull', 2, 13),
            ('room7', 'Salle Guido van Rossum', 3, 10),
            ('room8', 'Salle Haskell Curry', 3, 15),
            ('room9', 'Salle John von Neumann', 3, 40);
        """
    )

    # End the process:
    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_sqlite_db("workrooms_booking.db")
