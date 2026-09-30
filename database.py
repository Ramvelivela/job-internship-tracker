import sqlite3


def create_database():
    connection = sqlite3.connect("jobs.db")
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            role TEXT NOT NULL,
            location TEXT,
            link TEXT,
            status TEXT DEFAULT 'Pending'
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS internships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            role TEXT NOT NULL,
            location TEXT,
            link TEXT,
            status TEXT DEFAULT 'Pending'
        )
    """)

    # Add status column to existing jobs table if it doesn't exist
    cursor.execute("PRAGMA table_info(jobs)")
    job_columns = [column[1] for column in cursor.fetchall()]

    if "status" not in job_columns:
        cursor.execute(
            "ALTER TABLE jobs ADD COLUMN status TEXT DEFAULT 'Pending'"
        )

    # Add status column to existing internships table if it doesn't exist
    cursor.execute("PRAGMA table_info(internships)")
    internship_columns = [column[1] for column in cursor.fetchall()]

    if "status" not in internship_columns:
        cursor.execute(
            "ALTER TABLE internships ADD COLUMN status TEXT DEFAULT 'Pending'"
        )

    connection.commit()
    connection.close()


create_database()