from flask import Flask, render_template, request, redirect, send_from_directory, session
import sqlite3
import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from database import create_database

app = Flask(__name__)
create_database()
app.secret_key = "job_tracker_secret_key"

def login_required():
    if not session.get("logged_in"):
        return redirect("/login")

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

        connection = sqlite3.connect("jobs.db")
        cursor = connection.cursor()

        try:
            cursor.execute("""
                INSERT INTO users (username, email, password_hash)
                VALUES (?, ?, ?)
            """, (username, email, password_hash))

            connection.commit()

        except sqlite3.IntegrityError:
            connection.close()
            return "Username or email already exists"

        connection.close()

        return redirect("/login")

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username_or_email = request.form["username"]
        password = request.form["password"]

        connection = sqlite3.connect("jobs.db")
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()

        cursor.execute("""
            SELECT * FROM users
            WHERE username = ? OR email = ?
        """, (username_or_email, username_or_email))

        user = cursor.fetchone()
        connection.close()

        if user and check_password_hash(user["password_hash"], password):
            session["logged_in"] = True
            session["user_id"] = user["id"]
            session["username"] = user["username"]

            return redirect("/")

        return render_template(
            "login.html",
            error="Invalid username or password"
        )

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect("/login")


@app.route("/")
def home():

        check = login_required()
        if check:
            return check
        connection = sqlite3.connect("jobs.db")
        connection.row_factory = sqlite3.Row

        cursor = connection.cursor()

        cursor.execute(
            "SELECT * FROM jobs WHERE user_id = ?",
            (session["user_id"],)
        )
        jobs = cursor.fetchall()

        cursor.execute(
            "SELECT * FROM internships WHERE user_id = ?",
            (session["user_id"],)
        )
        internships = cursor.fetchall()

        connection.close()

        return render_template(
            "index.html",
            jobs=jobs,
            internships=internships
        )

@app.route("/delete-internship/<int:internship_id>")
def delete_internship(internship_id):
    check = login_required()
    if check:
        return check
    connection = sqlite3.connect("jobs.db")
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM internships WHERE id = ? AND user_id = ?",
        (internship_id, session["user_id"])
    )

    connection.commit()
    connection.close()

    return redirect("/")

@app.route("/edit-internship/<int:internship_id>", methods=["GET", "POST"])
def edit_internship(internship_id):
    check = login_required()
    if check:
        return check
    connection = sqlite3.connect("jobs.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    if request.method == "POST":
        company = request.form["company"]
        role = request.form["role"]
        location = request.form["location"]
        link = request.form["link"]
        status = request.form["status"]

        cursor.execute("""
            UPDATE internships
            SET company = ?, role = ?, location = ?, link = ?, status = ?
            WHERE id = ? AND user_id = ?
        """, (company, role, location, link, status, internship_id, session["user_id"]))

        connection.commit()
        connection.close()

        return redirect("/")

    cursor.execute(
        "SELECT * FROM internships WHERE id = ? AND user_id = ?",
        (internship_id, session["user_id"])
    )
    internship = cursor.fetchone()

    connection.close()

    return render_template(
        "edit_internship.html",
        internship=internship
    )


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


        connection = sqlite3.connect("jobs.db")
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO jobs (company, role, location, link, status, user_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (company, role, location, link, status, session["user_id"]))

        connection.commit()
        connection.close()

        return redirect("/")
    return render_template("add_job.html")

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

        connection = sqlite3.connect("jobs.db")
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO internships (company, role, location, link, status, user_id)
            VALUES (?, ?, ?, ?,?, ?)
        """, (company, role, location, link, status, session["user_id"]))

        connection.commit()
        connection.close()

        return redirect("/")

    return render_template("add_internship.html")


@app.route("/delete-job/<int:job_id>")
def delete_job(job_id):
    check = login_required()
    if check:
        return check
    connection = sqlite3.connect("jobs.db")
    cursor = connection.cursor()

    cursor.execute("DELETE FROM jobs WHERE id = ? AND user_id = ?", (job_id, session["user_id"]))

    connection.commit()
    connection.close()

    return redirect("/")


@app.route("/edit-job/<int:job_id>", methods=["GET", "POST"])
def edit_job(job_id):
    check = login_required()
    if check:
        return check
    connection = sqlite3.connect("jobs.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    if request.method == "POST":
        company = request.form["company"]
        role = request.form["role"]
        location = request.form["location"]
        link = request.form["link"]
        status = request.form["status"]

        cursor.execute("""
            UPDATE jobs
            SET company = ?, role = ?, location = ?, link = ?, status = ?
            WHERE id = ? AND user_id = ?
        """, (company, role, location, link, status, job_id, session["user_id"]))

        connection.commit()
        connection.close()

        return redirect("/")

    cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id, session["user_id"]))
    job = cursor.fetchone()

    connection.close()

    return render_template("edit_job.html", job=job)

    return render_template("add_job.html")

@app.route("/personal-details", methods=["GET", "POST"])
def personal_details():
    check = login_required()
    if check:
        return check

    connection = sqlite3.connect("jobs.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    if request.method == "POST":
        full_name = request.form["full_name"]
        phone = request.form["phone"]
        location = request.form["location"]
        bio = request.form["bio"]

        cursor.execute("""
            UPDATE users
            SET full_name = ?, phone = ?, location = ?, bio = ?
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

    cursor.execute(
        "SELECT * FROM users WHERE id = ?",
        (session["user_id"],)
    )

    user = cursor.fetchone()

    connection.close()

    return render_template(
        "personal_details.html",
        user=user
    )

@app.route("/profile", methods=["GET", "POST"])
def profile():
    check = login_required()
    if check:
        return check

    connection = sqlite3.connect("jobs.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    if request.method == "POST":
        full_name = request.form["full_name"]
        phone = request.form["phone"]
        location = request.form["location"]
        bio = request.form["bio"]

        cursor.execute("""
            UPDATE users
            SET full_name = ?, phone = ?, location = ?, bio = ?
            WHERE id = ?
        """, (
            full_name,
            phone,
            location,
            bio,
            session["user_id"]
        ))

        connection.commit()

    cursor.execute(
        "SELECT * FROM users WHERE id = ?",
        (session["user_id"],)
    )
    user = cursor.fetchone()
    # Calculate profile completion
    fields = [
        user["full_name"],
        user["phone"],
        user["location"],
        user["bio"]
    ]

    completed_fields = sum(
        1 for field in fields
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


@app.route("/resume")
def resume():
    check = login_required()
    if check:
        return check
    resumes = os.listdir("uploads")

    user_resume = [
        filename
        for filename in resumes
        if filename.startswith(f"user_{session['user_id']}_")
    ]

    current_resume = user_resume[0] if user_resume else None

    return render_template(
        "resume.html",
        current_resume=current_resume
    )


@app.route("/upload-resume", methods=["POST"])
def upload_resume():
    check = login_required()
    if check:
        return check
    if "resume" not in request.files:
        return redirect("/resume")

    file = request.files["resume"]

    if file.filename == "":
        return redirect("/resume")

    original_filename = secure_filename(file.filename)
    filename = f"user_{session['user_id']}_{original_filename}"

    # Delete existing resume
    for old_file in os.listdir("uploads"):
        if old_file.startswith(f"user_{session['user_id']}_"):
            old_path = os.path.join("uploads", old_file)

            if os.path.isfile(old_path):
                os.remove(old_path)

    # Save new resume
    file.save(os.path.join("uploads", filename))

    return redirect("/resume")

@app.route("/view-resume/<filename>")
def view_resume(filename):
    check = login_required()
    if check:
        return check
    if not filename.startswith(f"user_{session['user_id']}_"):
        return "Access denied", 403

    return send_from_directory("uploads", filename)

@app.route("/delete-resume", methods=["POST"])
def delete_resume():
    check = login_required()
    if check:
        return check
    for filename in os.listdir("uploads"):
        if filename.startswith(f"user_{session['user_id']}_"):
            file_path = os.path.join("uploads", filename)

            if os.path.isfile(file_path):
                os.remove(file_path)

    return redirect("/resume")


if __name__ == "__main__":
    app.run(debug=True)