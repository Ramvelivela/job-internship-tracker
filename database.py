import sqlite3


def create_database():
    connection = sqlite3.connect("jobs.db")
    cursor = connection.cursor()

    # ---------------- USERS ----------------

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
        cursor.execute("ALTER TABLE users ADD COLUMN full_name TEXT")

    if "phone" not in user_columns:
        cursor.execute("ALTER TABLE users ADD COLUMN phone TEXT")

    if "location" not in user_columns:
        cursor.execute("ALTER TABLE users ADD COLUMN location TEXT")

    if "bio" not in user_columns:
        cursor.execute("ALTER TABLE users ADD COLUMN bio TEXT")

    if "profile_picture" not in user_columns:
        cursor.execute("ALTER TABLE users ADD COLUMN profile_picture TEXT")

    # ---------------- JOBS ----------------

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

    cursor.execute("PRAGMA table_info(jobs)")
    job_columns = [column[1] for column in cursor.fetchall()]

    if "status" not in job_columns:
        cursor.execute(
            "ALTER TABLE jobs ADD COLUMN status TEXT DEFAULT 'Pending'"
        )

    if "user_id" not in job_columns:
        cursor.execute(
            "ALTER TABLE jobs ADD COLUMN user_id INTEGER"
        )

    # ---------------- INTERNSHIPS ----------------

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

    cursor.execute("PRAGMA table_info(internships)")
    internship_columns = [column[1] for column in cursor.fetchall()]

    if "status" not in internship_columns:
        cursor.execute(
            "ALTER TABLE internships ADD COLUMN status TEXT DEFAULT 'Pending'"
        )

    if "user_id" not in internship_columns:
        cursor.execute(
            "ALTER TABLE internships ADD COLUMN user_id INTEGER"
        )

    # ---------------- QUALIFICATIONS ----------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS qualifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            degree TEXT,
            branch TEXT,
            college TEXT,
            graduation_year TEXT,
            cgpa TEXT
        )
    """)

    # ---------------- JOB PREFERENCES ----------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS job_preferences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            preferred_role TEXT,
            preferred_location TEXT,
            employment_type TEXT,
            work_mode TEXT,
            expected_salary TEXT
        )
    """)

    connection.commit()
    connection.close()


create_database()