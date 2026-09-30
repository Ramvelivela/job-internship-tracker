from flask import Flask, render_template, request, redirect, send_from_directory
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)


@app.route("/")
def home():
    connection = sqlite3.connect("jobs.db")
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("SELECT * FROM jobs")
    jobs = cursor.fetchall()

    cursor.execute("SELECT * FROM internships")
    internships = cursor.fetchall()

    connection.close()

    return render_template(
        "index.html",
        jobs=jobs,
        internships=internships
    )

@app.route("/delete-internship/<int:internship_id>")
def delete_internship(internship_id):
    connection = sqlite3.connect("jobs.db")
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM internships WHERE id = ?",
        (internship_id,)
    )

    connection.commit()
    connection.close()

    return redirect("/")

@app.route("/edit-internship/<int:internship_id>", methods=["GET", "POST"])
def edit_internship(internship_id):
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
            WHERE id = ?
        """, (company, role, location, link, status, internship_id))

        connection.commit()
        connection.close()

        return redirect("/")

    cursor.execute(
        "SELECT * FROM internships WHERE id = ?",
        (internship_id,)
    )
    internship = cursor.fetchone()

    connection.close()

    return render_template(
        "edit_internship.html",
        internship=internship
    )


@app.route("/add-job", methods=["GET", "POST"])
def add_job():
    if request.method == "POST":
        company = request.form["company"]
        role = request.form["role"]
        location = request.form["location"]
        link = request.form["link"]
        status = request.form["status"]


        connection = sqlite3.connect("jobs.db")
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO jobs (company, role, location, link, status)
            VALUES (?, ?, ?, ?, ?)
        """, (company, role, location, link, status))

        connection.commit()
        connection.close()

        return redirect("/")
    return render_template("add_job.html")

@app.route("/add-internship", methods=["GET", "POST"])
def add_internship():
    if request.method == "POST":
        company = request.form["company"]
        role = request.form["role"]
        location = request.form["location"]
        link = request.form["link"]
        status = request.form["status"]

        connection = sqlite3.connect("jobs.db")
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO internships (company, role, location, link)
            VALUES (?, ?, ?, ?)
        """, (company, role, location, link, status))

        connection.commit()
        connection.close()

        return redirect("/")

    return render_template("add_internship.html")


@app.route("/delete-job/<int:job_id>")
def delete_job(job_id):
    connection = sqlite3.connect("jobs.db")
    cursor = connection.cursor()

    cursor.execute("DELETE FROM jobs WHERE id = ?", (job_id,))

    connection.commit()
    connection.close()

    return redirect("/")


@app.route("/edit-job/<int:job_id>", methods=["GET", "POST"])
def edit_job(job_id):
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
            WHERE id = ?
        """, (company, role, location, link, status, job_id))

        connection.commit()
        connection.close()

        return redirect("/")

    cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
    job = cursor.fetchone()

    connection.close()

    return render_template("edit_job.html", job=job)

    return render_template("add_job.html")


@app.route("/resume")
def resume():
    resumes = os.listdir("uploads")

    current_resume = resumes[0] if resumes else None

    return render_template(
        "resume.html",
        current_resume=current_resume
    )


@app.route("/upload-resume", methods=["POST"])
def upload_resume():
    if "resume" not in request.files:
        return redirect("/resume")

    file = request.files["resume"]

    if file.filename == "":
        return redirect("/resume")

    filename = secure_filename(file.filename)

    # Delete existing resume
    for old_file in os.listdir("uploads"):
        old_path = os.path.join("uploads", old_file)

        if os.path.isfile(old_path):
            os.remove(old_path)

    # Save new resume
    file.save(os.path.join("uploads", filename))

    return redirect("/resume")

@app.route("/view-resume/<filename>")
def view_resume(filename):
    return send_from_directory("uploads", filename)

@app.route("/delete-resume", methods=["POST"])
def delete_resume():
    for filename in os.listdir("uploads"):
        file_path = os.path.join("uploads", filename)

        if os.path.isfile(file_path):
            os.remove(file_path)

    return redirect("/resume")


if __name__ == "__main__":
    app.run(debug=True)