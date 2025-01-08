import sqlite3

DB_PATH = "db/data.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS inflation_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            keyRate REAL,
            infl REAL,
            targetInfl REAL
        )
    """
    )
    conn.commit()
    conn.close()


if __name__ == "__main__":
    initialize_database()
