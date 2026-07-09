"""
Smart Classroom for Rural Colleges - Backend
=============================================
A lightweight Flask + SQLite backend designed for low-bandwidth,
rural-college environments.

Features:
- Student & teacher records
- Course management
- Attendance marking & reports
- Study material / resource sharing (links to files, works offline once downloaded)
- Announcements board

Run:
    pip install -r requirements.txt
    python app.py

The server starts at http://127.0.0.1:5000
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Allows the frontend (opened as a separate file) to call this API

DB_PATH = os.path.join(os.path.dirname(__file__), "smart_classroom.db")


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll_no TEXT UNIQUE NOT NULL,
            village TEXT,
            phone TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            teacher TEXT,
            description TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            course_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('present', 'absent')),
            FOREIGN KEY(student_id) REFERENCES students(id),
            FOREIGN KEY(course_id) REFERENCES courses(id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            type TEXT NOT NULL,        -- 'pdf', 'video', 'link', 'note'
            url TEXT NOT NULL,
            uploaded_on TEXT NOT NULL,
            FOREIGN KEY(course_id) REFERENCES courses(id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS announcements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            posted_on TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "message": "Smart Classroom backend running"})


# ---------------------------------------------------------------------------
# Students
# ---------------------------------------------------------------------------
@app.route("/api/students", methods=["GET"])
def get_students():
    conn = get_db()
    rows = conn.execute("SELECT * FROM students ORDER BY name").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/students", methods=["POST"])
def add_student():
    data = request.get_json(force=True)
    name = data.get("name")
    roll_no = data.get("roll_no")
    village = data.get("village", "")
    phone = data.get("phone", "")

    if not name or not roll_no:
        return jsonify({"error": "name and roll_no are required"}), 400

    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO students (name, roll_no, village, phone) VALUES (?, ?, ?, ?)",
            (name, roll_no, village, phone),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"error": "roll_no already exists"}), 409
    conn.close()
    return jsonify({"message": "Student added"}), 201


# ---------------------------------------------------------------------------
# Courses
# ---------------------------------------------------------------------------
@app.route("/api/courses", methods=["GET"])
def get_courses():
    conn = get_db()
    rows = conn.execute("SELECT * FROM courses ORDER BY title").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/courses", methods=["POST"])
def add_course():
    data = request.get_json(force=True)
    title = data.get("title")
    teacher = data.get("teacher", "")
    description = data.get("description", "")

    if not title:
        return jsonify({"error": "title is required"}), 400

    conn = get_db()
    conn.execute(
        "INSERT INTO courses (title, teacher, description) VALUES (?, ?, ?)",
        (title, teacher, description),
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Course added"}), 201


# ---------------------------------------------------------------------------
# Attendance
# ---------------------------------------------------------------------------
@app.route("/api/attendance", methods=["POST"])
def mark_attendance():
    data = request.get_json(force=True)
    student_id = data.get("student_id")
    course_id = data.get("course_id")
    status = data.get("status")
    date = data.get("date") or datetime.now().strftime("%Y-%m-%d")

    if not student_id or not course_id or status not in ("present", "absent"):
        return jsonify({"error": "student_id, course_id and valid status are required"}), 400

    conn = get_db()
    conn.execute(
        "INSERT INTO attendance (student_id, course_id, date, status) VALUES (?, ?, ?, ?)",
        (student_id, course_id, date, status),
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Attendance recorded"}), 201


@app.route("/api/attendance/<int:course_id>", methods=["GET"])
def get_attendance(course_id):
    conn = get_db()
    rows = conn.execute("""
        SELECT a.id, a.date, a.status, s.name, s.roll_no
        FROM attendance a
        JOIN students s ON s.id = a.student_id
        WHERE a.course_id = ?
        ORDER BY a.date DESC
    """, (course_id,)).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


# ---------------------------------------------------------------------------
# Resources (study material)
# ---------------------------------------------------------------------------
@app.route("/api/resources/<int:course_id>", methods=["GET"])
def get_resources(course_id):
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM resources WHERE course_id = ? ORDER BY uploaded_on DESC",
        (course_id,),
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/resources", methods=["POST"])
def add_resource():
    data = request.get_json(force=True)
    course_id = data.get("course_id")
    title = data.get("title")
    rtype = data.get("type", "note")
    url = data.get("url")

    if not course_id or not title or not url:
        return jsonify({"error": "course_id, title and url are required"}), 400

    conn = get_db()
    conn.execute(
        "INSERT INTO resources (course_id, title, type, url, uploaded_on) VALUES (?, ?, ?, ?, ?)",
        (course_id, title, rtype, url, datetime.now().strftime("%Y-%m-%d %H:%M")),
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Resource added"}), 201


# ---------------------------------------------------------------------------
# Announcements
# ---------------------------------------------------------------------------
@app.route("/api/announcements", methods=["GET"])
def get_announcements():
    conn = get_db()
    rows = conn.execute("SELECT * FROM announcements ORDER BY posted_on DESC").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/announcements", methods=["POST"])
def add_announcement():
    data = request.get_json(force=True)
    title = data.get("title")
    message = data.get("message")

    if not title or not message:
        return jsonify({"error": "title and message are required"}), 400

    conn = get_db()
    conn.execute(
        "INSERT INTO announcements (title, message, posted_on) VALUES (?, ?, ?)",
        (title, message, datetime.now().strftime("%Y-%m-%d %H:%M")),
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Announcement posted"}), 201


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    init_db()
    print("Smart Classroom backend starting at http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
