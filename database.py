import sqlite3


def create_database():
    connection = sqlite3.connect("jobs.db")
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)

    cursor.execute("PRAGMA table_info(users)")
    user_columns = [column[1] for column in cursor.fetchall()]

    if "full_name" not in user_columns:
        cursor.execute(
            "ALTER TABLE users ADD COLUMN full_name TEXT"
        )

    if "phone" not in user_columns:
        cursor.execute(
            "ALTER TABLE users ADD COLUMN phone TEXT"
        )

    if "location" not in user_columns:
        cursor.execute(
            "ALTER TABLE users ADD COLUMN location TEXT"
        )

    if "bio" not in user_columns:
        cursor.execute(
            "ALTER TABLE users ADD COLUMN bio TEXT"
        )

    if "profile_picture" not in user_columns:
        cursor.execute(
            "ALTER TABLE users ADD COLUMN profile_picture TEXT"
        )

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

    # Add user_id column to existing jobs table
    if "user_id" not in job_columns:
        cursor.execute(
        "ALTER TABLE jobs ADD COLUMN user_id INTEGER"
        )

    # Add user_id column to existing internships table
    cursor.execute("PRAGMA table_info(internships)")
    internship_columns = [column[1] for column in cursor.fetchall()]

    if "user_id" not in internship_columns:
        cursor.execute(
            "ALTER TABLE internships ADD COLUMN user_id INTEGER"
        )

    connection.commit()
    connection.close()


create_database()