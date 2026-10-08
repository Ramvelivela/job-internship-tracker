import os
import sqlite3


def create_database():
    database_url = os.getenv("DATABASE_URL")

    # ==============================
    # RENDER → POSTGRESQL
    # ==============================
    if database_url:
        import psycopg

        connection = psycopg.connect(database_url)
        cursor = connection.cursor()

        # ---------------- USERS ----------------
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT,
                phone TEXT,
                location TEXT,
                bio TEXT,
                profile_picture TEXT
            )
        """)
        # ---------------- PASSWORD RESET ----------------

        cursor.execute("""
            ALTER TABLE users
            ADD COLUMN IF NOT EXISTS reset_token TEXT
        """)

        cursor.execute("""
            ALTER TABLE users
            ADD COLUMN IF NOT EXISTS reset_token_expiry TEXT
        """)

        # ---------------- JOBS ----------------
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id SERIAL PRIMARY KEY,
                company TEXT NOT NULL,
                role TEXT NOT NULL,
                location TEXT,
                link TEXT,
                status TEXT DEFAULT 'Pending',
                user_id INTEGER
            )
        """)

        # ---------------- JOBS MIGRATION ----------------

        cursor.execute("""
            ALTER TABLE jobs
            ADD COLUMN IF NOT EXISTS application_date DATE
        """)

        cursor.execute("""
            ALTER TABLE jobs
            ADD COLUMN IF NOT EXISTS deadline DATE
        """)

        cursor.execute("""
            ALTER TABLE jobs
            ADD COLUMN IF NOT EXISTS interview_date DATE
        """)

        cursor.execute("""
            ALTER TABLE jobs
            ADD COLUMN IF NOT EXISTS follow_up_date DATE
        """)

        cursor.execute("""
            ALTER TABLE jobs
            ADD COLUMN IF NOT EXISTS notes TEXT
        """)

        # ---------------- INTERNSHIPS ----------------
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS internships (
                id SERIAL PRIMARY KEY,
                company TEXT NOT NULL,
                role TEXT NOT NULL,
                location TEXT,
                link TEXT,
                status TEXT DEFAULT 'Pending',
                user_id INTEGER
            )
        """)
        # ---------------- INTERNSHIPS MIGRATION ----------------

        cursor.execute("""
            ALTER TABLE internships
            ADD COLUMN IF NOT EXISTS application_date DATE
        """)

        cursor.execute("""
            ALTER TABLE internships
            ADD COLUMN IF NOT EXISTS deadline DATE
        """)

        cursor.execute("""
            ALTER TABLE internships
            ADD COLUMN IF NOT EXISTS interview_date DATE
        """)

        cursor.execute("""
            ALTER TABLE internships
            ADD COLUMN IF NOT EXISTS follow_up_date DATE
        """)

        cursor.execute("""
            ALTER TABLE internships
            ADD COLUMN IF NOT EXISTS notes TEXT
        """)
        # ---------------- RESUME BUILDER -----------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS resume_builder (
                id SERIAL PRIMARY KEY,
                user_id INTEGER UNIQUE NOT NULL,
                skills TEXT,
                projects TEXT,
                certifications TEXT,
                achievements TEXT
            )
        """)

        # ---------------- QUALIFICATIONS ----------------
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS qualifications (
                id SERIAL PRIMARY KEY,
                user_id INTEGER UNIQUE NOT NULL,
                degree TEXT,
                branch TEXT,
                college TEXT,
                graduation_year TEXT,
                cgpa TEXT
            )
        """)
        # ---------------- QUALIFICATIONS MIGRATION ----------------

        cursor.execute("""
            ALTER TABLE qualifications
            ADD COLUMN IF NOT EXISTS intermediate_college TEXT
        """)

        cursor.execute("""
            ALTER TABLE qualifications
            ADD COLUMN IF NOT EXISTS intermediate_percentage TEXT
        """)

        cursor.execute("""
            ALTER TABLE qualifications
            ADD COLUMN IF NOT EXISTS ssc_school TEXT
        """)

        cursor.execute("""
            ALTER TABLE qualifications
            ADD COLUMN IF NOT EXISTS ssc_percentage TEXT
        """)

        # ---------------- JOB PREFERENCES ----------------
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS job_preferences (
                id SERIAL PRIMARY KEY,
                user_id INTEGER UNIQUE NOT NULL,
                preferred_role TEXT,
                preferred_location TEXT,
                employment_type TEXT,
                work_mode TEXT,
                expected_salary TEXT
            )
        """)

        connection.commit()
        cursor.close()
        connection.close()

        return

    # ==============================
    # LOCAL → SQLITE
    # ==============================
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

    # ---------------- PASSWORD RESET ----------------

    if "reset_token" not in user_columns:
        cursor.execute(
            "ALTER TABLE users ADD COLUMN reset_token TEXT"
        )

    if "reset_token_expiry" not in user_columns:
        cursor.execute(
            "ALTER TABLE users ADD COLUMN reset_token_expiry TEXT"
        )

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

    if "application_date" not in job_columns:
        cursor.execute(
            "ALTER TABLE jobs ADD COLUMN application_date DATE"
        )

    if "deadline" not in job_columns:
        cursor.execute(
            "ALTER TABLE jobs ADD COLUMN deadline DATE"
        )

    if "interview_date" not in job_columns:
        cursor.execute(
            "ALTER TABLE jobs ADD COLUMN interview_date DATE"
        )

    if "follow_up_date" not in job_columns:
        cursor.execute(
            "ALTER TABLE jobs ADD COLUMN follow_up_date DATE"
        )

    if "notes" not in job_columns:
        cursor.execute(
            "ALTER TABLE jobs ADD COLUMN notes TEXT"
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
    if "application_date" not in internship_columns:
        cursor.execute(
            "ALTER TABLE internships ADD COLUMN application_date DATE"
        )

    if "deadline" not in internship_columns:
        cursor.execute(
            "ALTER TABLE internships ADD COLUMN deadline DATE"
        )

    if "interview_date" not in internship_columns:
        cursor.execute(
            "ALTER TABLE internships ADD COLUMN interview_date DATE"
        )

    if "follow_up_date" not in internship_columns:
        cursor.execute(
            "ALTER TABLE internships ADD COLUMN follow_up_date DATE"
        )

    if "notes" not in internship_columns:
        cursor.execute(
            "ALTER TABLE internships ADD COLUMN notes TEXT"
        )

    # ---------------- RESUME BUILDER ----------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resume_builder (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            skills TEXT,
            projects TEXT,
            certifications TEXT,
            achievements TEXT
        )
    """)

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

    cursor.execute("PRAGMA table_info(qualifications)")
    qualification_columns = [
        column[1] for column in cursor.fetchall()
    ]

    if "intermediate_college" not in qualification_columns:
        cursor.execute(
            "ALTER TABLE qualifications ADD COLUMN intermediate_college TEXT"
        )

    if "intermediate_percentage" not in qualification_columns:
        cursor.execute(
            "ALTER TABLE qualifications ADD COLUMN intermediate_percentage TEXT"
        )

    if "ssc_school" not in qualification_columns:
        cursor.execute(
            "ALTER TABLE qualifications ADD COLUMN ssc_school TEXT"
        )

    if "ssc_percentage" not in qualification_columns:
        cursor.execute(
            "ALTER TABLE qualifications ADD COLUMN ssc_percentage TEXT"
        )

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