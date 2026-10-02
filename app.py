from flask import (
    Flask,
    render_template,
    request,
    redirect,
    send_from_directory,
    session
)

import sqlite3
import os

import psycopg
from psycopg.rows import dict_row

from werkzeug.utils import secure_filename
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from database import create_database


app = Flask(__name__)
app.secret_key = "job_tracker_secret_key"


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_connection():
    database_url = os.getenv("DATABASE_URL")

    # Render / PostgreSQL
    if database_url:
        return psycopg.connect(
            database_url,
            cursor_factory=RealDictCursor
        )

    # Local / SQLite
    connection = sqlite3.connect("jobs.db")
    connection.row_factory = sqlite3.Row
    return connection


def db_execute(cursor, query, params=()):
    """
    SQLite uses ?
    PostgreSQL uses %s

    This helper automatically converts ? to %s
    when running on PostgreSQL.
    """
    if os.getenv("DATABASE_URL"):
        query = query.replace("?", "%s")

    cursor.execute(query, params)


# =========================================================
# DATABASE INITIALIZATION
# =========================================================

def initialize_database():
    """
    Local:
        Uses existing database.py SQLite setup.

    Render:
        Creates PostgreSQL tables.
    """

    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        create_database()
        return

    connection = get_connection()
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
    connection.close()


# Create database/tables when application starts
initialize_database()


# Make sure uploads folder exists
os.makedirs("uploads", exist_ok=True)


# =========================================================
# LOGIN REQUIRED
# =========================================================

def login_required():
    if not session.get("logged_in"):
        return redirect("/login")


# =========================================================
# REGISTER
# =========================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            return "Passwords do not match"

        password_hash = generate_password_hash(password)

        connection = get_connection()
        cursor = connection.cursor()

        try:

            db_execute(cursor, """
                INSERT INTO users (
                    username,
                    email,
                    password_hash
                )
                VALUES (?, ?, ?)
            """, (
                username,
                email,
                password_hash
            ))

            connection.commit()

        except (sqlite3.IntegrityError, psycopg.IntegrityError):

            connection.rollback()
            connection.close()

            return "Username or email already exists"

        connection.close()

        return redirect("/login")

    return render_template("register.html")


# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username_or_email = request.form["username"]
        password = request.form["password"]

        connection = get_connection()
        cursor = connection.cursor()

        db_execute(cursor, """
            SELECT *
            FROM users
            WHERE username = ?
               OR email = ?
        """, (
            username_or_email,
            username_or_email
        ))

        user = cursor.fetchone()

        connection.close()

        if user and check_password_hash(
            user["password_hash"],
            password
        ):

            session["logged_in"] = True
            session["user_id"] = user["id"]
            session["username"] = user["username"]

            return redirect("/")

        return render_template(
            "login.html",
            error="Invalid username or password"
        )

    return render_template("login.html")


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/")
def home():

    check = login_required()

    if check:
        return check

    connection = get_connection()
    cursor = connection.cursor()

    db_execute(cursor, """
        SELECT *
        FROM jobs
        WHERE user_id = ?
    """, (
        session["user_id"],
    ))

    jobs = cursor.fetchall()

    db_execute(cursor, """
        SELECT *
        FROM internships
        WHERE user_id = ?
    """, (
        session["user_id"],
    ))

    internships = cursor.fetchall()

    connection.close()

    return render_template(
        "index.html",
        jobs=jobs,
        internships=internships
    )


# =========================================================
# ADD JOB
# =========================================================

@app.route("/add-job", methods=["GET", "POST"])
def add_job():

    check = login_required()

    if check:
        return check

    if request.method == "POST":

        company = request.form["company"]
        role = request.form["role"]
        location = request.form["location"]
        link = request.form["link"]
        status = request.form["status"]

        connection = get_connection()
        cursor = connection.cursor()

        db_execute(cursor, """
            INSERT INTO jobs (
                company,
                role,
                location,
                link,
                status,
                user_id
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            company,
            role,
            location,
            link,
            status,
            session["user_id"]
        ))

        connection.commit()
        connection.close()

        return redirect("/")

    return render_template("add_job.html")


# =========================================================
# ADD INTERNSHIP
# =========================================================

@app.route("/add-internship", methods=["GET", "POST"])
def add_internship():

    check = login_required()

    if check:
        return check

    if request.method == "POST":

        company = request.form["company"]
        role = request.form["role"]
        location = request.form["location"]
        link = request.form["link"]
        status = request.form["status"]

        connection = get_connection()
        cursor = connection.cursor()

        db_execute(cursor, """
            INSERT INTO internships (
                company,
                role,
                location,
                link,
                status,
                user_id
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            company,
            role,
            location,
            link,
            status,
            session["user_id"]
        ))

        connection.commit()
        connection.close()

        return redirect("/")

    return render_template("add_internship.html")


# =========================================================
# DELETE JOB
# =========================================================

@app.route("/delete-job/<int:job_id>")
def delete_job(job_id):

    check = login_required()

    if check:
        return check

    connection = get_connection()
    cursor = connection.cursor()

    db_execute(cursor, """
        DELETE FROM jobs
        WHERE id = ?
          AND user_id = ?
    """, (
        job_id,
        session["user_id"]
    ))

    connection.commit()
    connection.close()

    return redirect("/")


# =========================================================
# DELETE INTERNSHIP
# =========================================================

@app.route("/delete-internship/<int:internship_id>")
def delete_internship(internship_id):

    check = login_required()

    if check:
        return check

    connection = get_connection()
    cursor = connection.cursor()

    db_execute(cursor, """
        DELETE FROM internships
        WHERE id = ?
          AND user_id = ?
    """, (
        internship_id,
        session["user_id"]
    ))

    connection.commit()
    connection.close()

    return redirect("/")


# =========================================================
# EDIT JOB
# =========================================================

@app.route("/edit-job/<int:job_id>", methods=["GET", "POST"])
def edit_job(job_id):

    check = login_required()

    if check:
        return check

    connection = get_connection()
    cursor = connection.cursor()

    if request.method == "POST":

        company = request.form["company"]
        role = request.form["role"]
        location = request.form["location"]
        link = request.form["link"]
        status = request.form["status"]

        db_execute(cursor, """
            UPDATE jobs
            SET company = ?,
                role = ?,
                location = ?,
                link = ?,
                status = ?
            WHERE id = ?
              AND user_id = ?
        """, (
            company,
            role,
            location,
            link,
            status,
            job_id,
            session["user_id"]
        ))

        connection.commit()
        connection.close()

        return redirect("/")

    db_execute(cursor, """
        SELECT *
        FROM jobs
        WHERE id = ?
          AND user_id = ?
    """, (
        job_id,
        session["user_id"]
    ))

    job = cursor.fetchone()

    connection.close()

    return render_template(
        "edit_job.html",
        job=job
    )


# =========================================================
# EDIT INTERNSHIP
# =========================================================

@app.route(
    "/edit-internship/<int:internship_id>",
    methods=["GET", "POST"]
)
def edit_internship(internship_id):

    check = login_required()

    if check:
        return check

    connection = get_connection()
    cursor = connection.cursor()

    if request.method == "POST":

        company = request.form["company"]
        role = request.form["role"]
        location = request.form["location"]
        link = request.form["link"]
        status = request.form["status"]

        db_execute(cursor, """
            UPDATE internships
            SET company = ?,
                role = ?,
                location = ?,
                link = ?,
                status = ?
            WHERE id = ?
              AND user_id = ?
        """, (
            company,
            role,
            location,
            link,
            status,
            internship_id,
            session["user_id"]
        ))

        connection.commit()
        connection.close()

        return redirect("/")

    db_execute(cursor, """
        SELECT *
        FROM internships
        WHERE id = ?
          AND user_id = ?
    """, (
        internship_id,
        session["user_id"]
    ))

    internship = cursor.fetchone()

    connection.close()

    return render_template(
        "edit_internship.html",
        internship=internship
    )


# =========================================================
# PROFILE
# =========================================================

@app.route("/profile", methods=["GET", "POST"])
def profile():

    check = login_required()

    if check:
        return check

    connection = get_connection()
    cursor = connection.cursor()

    db_execute(cursor, """
        SELECT *
        FROM users
        WHERE id = ?
    """, (
        session["user_id"],
    ))

    user = cursor.fetchone()

    if user is None:

        session.clear()
        connection.close()

        return redirect("/login")

    if request.method == "POST":

        full_name = request.form["full_name"]
        phone = request.form["phone"]
        location = request.form["location"]
        bio = request.form["bio"]

        db_execute(cursor, """
            UPDATE users
            SET full_name = ?,
                phone = ?,
                location = ?,
                bio = ?
            WHERE id = ?
        """, (
            full_name,
            phone,
            location,
            bio,
            session["user_id"]
        ))

        connection.commit()

        db_execute(cursor, """
            SELECT *
            FROM users
            WHERE id = ?
        """, (
            session["user_id"],
        ))

        user = cursor.fetchone()

    fields = [
        user["full_name"],
        user["phone"],
        user["location"],
        user["bio"]
    ]

    completed_fields = sum(
        1
        for field in fields
        if field and field.strip()
    )

    completion = int(
        (completed_fields / len(fields)) * 100
    )

    connection.close()

    return render_template(
        "profile.html",
        user=user,
        completion=completion
    )


# =========================================================
# PERSONAL DETAILS
# =========================================================

@app.route(
    "/personal-details",
    methods=["GET", "POST"]
)
def personal_details():

    check = login_required()

    if check:
        return check

    connection = get_connection()
    cursor = connection.cursor()

    if request.method == "POST":

        full_name = request.form["full_name"]
        phone = request.form["phone"]
        location = request.form["location"]
        bio = request.form["bio"]

        db_execute(cursor, """
            UPDATE users
            SET full_name = ?,
                phone = ?,
                location = ?,
                bio = ?
            WHERE id = ?
        """, (
            full_name,
            phone,
            location,
            bio,
            session["user_id"]
        ))

        connection.commit()
        connection.close()

        return redirect("/profile")

    db_execute(cursor, """
        SELECT *
        FROM users
        WHERE id = ?
    """, (
        session["user_id"],
    ))

    user = cursor.fetchone()

    connection.close()

    return render_template(
        "personal_details.html",
        user=user
    )


# =========================================================
# QUALIFICATIONS
# =========================================================

@app.route(
    "/qualifications",
    methods=["GET", "POST"]
)
def qualifications():

    check = login_required()

    if check:
        return check

    connection = get_connection()
    cursor = connection.cursor()

    if request.method == "POST":

        degree = request.form["degree"]
        branch = request.form["branch"]
        college = request.form["college"]
        graduation_year = request.form["graduation_year"]
        cgpa = request.form["cgpa"]

        db_execute(cursor, """
            SELECT id
            FROM qualifications
            WHERE user_id = ?
        """, (
            session["user_id"],
        ))

        existing = cursor.fetchone()

        if existing:

            db_execute(cursor, """
                UPDATE qualifications
                SET degree = ?,
                    branch = ?,
                    college = ?,
                    graduation_year = ?,
                    cgpa = ?
                WHERE user_id = ?
            """, (
                degree,
                branch,
                college,
                graduation_year,
                cgpa,
                session["user_id"]
            ))

        else:

            db_execute(cursor, """
                INSERT INTO qualifications (
                    user_id,
                    degree,
                    branch,
                    college,
                    graduation_year,
                    cgpa
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                session["user_id"],
                degree,
                branch,
                college,
                graduation_year,
                cgpa
            ))

        connection.commit()
        connection.close()

        return redirect("/profile")

    db_execute(cursor, """
        SELECT *
        FROM qualifications
        WHERE user_id = ?
    """, (
        session["user_id"],
    ))

    qualification = cursor.fetchone()

    connection.close()

    return render_template(
        "qualifications.html",
        qualification=qualification
    )


# =========================================================
# JOB PREFERENCES
# =========================================================

@app.route(
    "/job-preferences",
    methods=["GET", "POST"]
)
def job_preferences():

    check = login_required()

    if check:
        return check

    connection = get_connection()
    cursor = connection.cursor()

    if request.method == "POST":

        preferred_role = request.form["preferred_role"]
        preferred_location = request.form["preferred_location"]
        employment_type = request.form["employment_type"]
        work_mode = request.form["work_mode"]
        expected_salary = request.form["expected_salary"]

        db_execute(cursor, """
            SELECT id
            FROM job_preferences
            WHERE user_id = ?
        """, (
            session["user_id"],
        ))

        existing = cursor.fetchone()

        if existing:

            db_execute(cursor, """
                UPDATE job_preferences
                SET preferred_role = ?,
                    preferred_location = ?,
                    employment_type = ?,
                    work_mode = ?,
                    expected_salary = ?
                WHERE user_id = ?
            """, (
                preferred_role,
                preferred_location,
                employment_type,
                work_mode,
                expected_salary,
                session["user_id"]
            ))

        else:

            db_execute(cursor, """
                INSERT INTO job_preferences (
                    user_id,
                    preferred_role,
                    preferred_location,
                    employment_type,
                    work_mode,
                    expected_salary
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                session["user_id"],
                preferred_role,
                preferred_location,
                employment_type,
                work_mode,
                expected_salary
            ))

        connection.commit()
        connection.close()

        return redirect("/profile")

    db_execute(cursor, """
        SELECT *
        FROM job_preferences
        WHERE user_id = ?
    """, (
        session["user_id"],
    ))

    preferences = cursor.fetchone()

    connection.close()

    return render_template(
        "job_preferences.html",
        preferences=preferences
    )


# =========================================================
# PROFILE SETTINGS
# =========================================================

@app.route(
    "/profile-settings",
    methods=["GET", "POST"]
)
def profile_settings():

    check = login_required()

    if check:
        return check

    connection = get_connection()
    cursor = connection.cursor()

    error = None

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]

        try:

            db_execute(cursor, """
                UPDATE users
                SET username = ?,
                    email = ?
                WHERE id = ?
            """, (
                username,
                email,
                session["user_id"]
            ))

            connection.commit()

            session["username"] = username

        except (
            sqlite3.IntegrityError,
            psycopg.IntegrityError
        ):

            connection.rollback()

            error = "Username or email already exists."

    db_execute(cursor, """
        SELECT *
        FROM users
        WHERE id = ?
    """, (
        session["user_id"],
    ))

    user = cursor.fetchone()

    connection.close()

    return render_template(
        "profile_settings.html",
        user=user,
        error=error
    )


# =========================================================
# CHANGE PASSWORD
# =========================================================

@app.route(
    "/change-password",
    methods=["GET", "POST"]
)
def change_password():

    check = login_required()

    if check:
        return check

    error = None
    success = None

    if request.method == "POST":

        current_password = request.form["current_password"]
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]

        connection = get_connection()
        cursor = connection.cursor()

        db_execute(cursor, """
            SELECT *
            FROM users
            WHERE id = ?
        """, (
            session["user_id"],
        ))

        user = cursor.fetchone()

        if user is None:

            connection.close()
            session.clear()

            return redirect("/login")

        if not check_password_hash(
            user["password_hash"],
            current_password
        ):

            error = "Current password is incorrect."

        elif new_password != confirm_password:

            error = "New passwords do not match."

        elif len(new_password) < 6:

            error = "New password must be at least 6 characters."

        else:

            new_password_hash = generate_password_hash(
                new_password
            )

            db_execute(cursor, """
                UPDATE users
                SET password_hash = ?
                WHERE id = ?
            """, (
                new_password_hash,
                session["user_id"]
            ))

            connection.commit()

            success = "Password changed successfully."

        connection.close()

    return render_template(
        "change_password.html",
        error=error,
        success=success
    )


# =========================================================
# RESUME
# =========================================================

@app.route("/resume")
def resume():

    check = login_required()

    if check:
        return check

    resumes = os.listdir("uploads")

    user_resume = [
        filename
        for filename in resumes
        if filename.startswith(
            f"user_{session['user_id']}_"
        )
    ]

    current_resume = (
        user_resume[0]
        if user_resume
        else None
    )

    return render_template(
        "resume.html",
        current_resume=current_resume
    )


# =========================================================
# UPLOAD RESUME
# =========================================================

@app.route(
    "/upload-resume",
    methods=["POST"]
)
def upload_resume():

    check = login_required()

    if check:
        return check

    if "resume" not in request.files:
        return redirect("/resume")

    file = request.files["resume"]

    if file.filename == "":
        return redirect("/resume")

    original_filename = secure_filename(
        file.filename
    )

    filename = (
        f"user_{session['user_id']}_"
        f"{original_filename}"
    )

    # Delete old resume for this user
    for old_file in os.listdir("uploads"):

        if old_file.startswith(
            f"user_{session['user_id']}_"
        ):

            old_path = os.path.join(
                "uploads",
                old_file
            )

            if os.path.isfile(old_path):
                os.remove(old_path)

    file.save(
        os.path.join(
            "uploads",
            filename
        )
    )

    return redirect("/resume")


# =========================================================
# VIEW RESUME
# =========================================================

@app.route(
    "/view-resume/<filename>"
)
def view_resume(filename):

    check = login_required()

    if check:
        return check

    if not filename.startswith(
        f"user_{session['user_id']}_"
    ):

        return "Access denied", 403

    return send_from_directory(
        "uploads",
        filename
    )


# =========================================================
# DELETE RESUME
# =========================================================

@app.route(
    "/delete-resume",
    methods=["POST"]
)
def delete_resume():

    check = login_required()

    if check:
        return check

    for filename in os.listdir("uploads"):

        if filename.startswith(
            f"user_{session['user_id']}_"
        ):

            file_path = os.path.join(
                "uploads",
                filename
            )

            if os.path.isfile(file_path):
                os.remove(file_path)

    return redirect("/resume")


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":
    app.run(debug=True)