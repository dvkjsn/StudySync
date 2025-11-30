from flask import (
    Flask, render_template, request,
    redirect, url_for, session, flash
)
from db import get_db_connection

app = Flask(__name__)
app.secret_key = "change_this_secret_string"


# ---------- helper: login_required ----------
def login_required(view_func):
    def wrapper(*args, **kwargs):
        if "email" not in session:
            flash("Please log in first.", "auth")
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


# ---------- HOME ----------
@app.route("/")
def index():
    return render_template("index.html")


# ---------- REGISTER ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        if not email or not password:
            flash("Email and password are required.", "auth")
            return redirect(url_for("register"))

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT email FROM Students WHERE email = ?", (email,))
        if cur.fetchone():
            flash("Account already exists.", "auth")
            conn.close()
            return redirect(url_for("login"))

        cur.execute("""
            INSERT INTO Students
              (email, password, first_name, last_name, major, class_year, preferred_mode)
            VALUES (?, ?, NULL, NULL, NULL, NULL, NULL)
        """, (email, password))

        conn.commit()
        conn.close()

        flash("Registration successful. Please log in.", "auth")
        return redirect(url_for("login"))

    return render_template("register.html")


# ---------- LOGIN ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT password FROM Students WHERE email = ?", (email,))
        row = cur.fetchone()
        conn.close()

        if row is None:
            flash("No account found with that email.", "auth")
            return redirect(url_for("login"))

        if row["password"] != password:
            flash("Incorrect password.", "auth")
            return redirect(url_for("login"))

        session["email"] = email
        flash("Welcome back!", "auth")
        return redirect(url_for("index"))

    return render_template("login.html")


# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out.", "auth")
    return redirect(url_for("index"))


# ---------- PROFILE ----------
@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    email = session["email"]

    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        major = request.form.get("major", "").strip()
        year = request.form.get("year", "").strip()
        preferred_mode = request.form.get("preferred_mode", "").strip()

        # split full name
        first_name = ""
        last_name = ""
        if full_name:
            parts = full_name.split(None, 1)
            first_name = parts[0]
            if len(parts) == 2:
                last_name = parts[1]

        cur.execute("""
            UPDATE Students
            SET first_name = ?, last_name = ?, major = ?, class_year = ?, preferred_mode = ?
            WHERE email = ?
        """, (first_name, last_name, major, year, preferred_mode, email))

        conn.commit()
        conn.close()

        flash("Profile updated.", "profile")
        return redirect(url_for("profile"))

    # GET: fetch data to prefill
    cur.execute("SELECT * FROM Students WHERE email = ?", (email,))
    student = cur.fetchone()
    conn.close()

    return render_template("profile.html", student=student)


# ---------- AVAILABILITY ----------
@app.route("/availability", methods=["GET", "POST"])
@login_required
def availability():
    email = session["email"]
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == "POST":
        day = request.form.get("day")
        start = request.form.get("start")
        end = request.form.get("end")

        cur.execute("SELECT MAX(SUBSTR(availability_id, 2)) AS max_id FROM Availability")
        result = cur.fetchone()["max_id"]
        next_num = (int(result) if result else 0) + 1
        availability_id = f"A{next_num:03d}"

        cur.execute("""
            INSERT INTO Availability
              (availability_id, email, day_of_week, start_time, end_time)
            VALUES (?, ?, ?, ?, ?)
        """, (availability_id, email, day, start, end))

        conn.commit()
        flash("Availability added.", "availability")

    cur.execute("""
        SELECT availability_id, day_of_week, start_time, end_time
        FROM Availability
        WHERE email = ?
        ORDER BY day_of_week, start_time
    """, (email,))
    rows = cur.fetchall()
    conn.close()

    return render_template("availability.html", availability=rows)


@app.route("/availability/delete/<availability_id>")
@login_required
def delete_availability(availability_id):
    email = session["email"]
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM Availability WHERE availability_id = ? AND email = ?",
        (availability_id, email),
    )
    conn.commit()
    conn.close()
    flash("Availability removed.", "availability")
    return redirect(url_for("availability"))


# ---------- ADD COURSES ----------
@app.route("/add_courses", methods=["GET", "POST"])
@login_required
def add_courses():
    email = session["email"]
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == "POST":
        course_id = request.form.get("course_id")
        cur.execute(
            "SELECT 1 FROM Enrollments WHERE email = ? AND course_id = ?",
            (email, course_id),
        )
        if cur.fetchone():
            flash("Already enrolled.", "courses")
        else:
            cur.execute(
                "INSERT INTO Enrollments (email, course_id) VALUES (?, ?)",
                (email, course_id),
            )
            conn.commit()
            flash("Course added.", "courses")

    cur.execute("SELECT * FROM Courses ORDER BY subject, course_number")
    all_courses = cur.fetchall()

    cur.execute("""
        SELECT c.course_id, c.subject, c.course_number, c.title
        FROM Enrollments e
        JOIN Courses c ON e.course_id = c.course_id
        WHERE e.email = ?
        ORDER BY c.subject, c.course_number
    """, (email,))
    my_courses = cur.fetchall()

    conn.close()
    return render_template("add_courses.html",
                           all_courses=all_courses,
                           my_courses=my_courses)


@app.route("/remove_course/<course_id>")
@login_required
def remove_course(course_id):
    email = session["email"]
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM Enrollments WHERE email = ? AND course_id = ?",
        (email, course_id),
    )
    conn.commit()
    conn.close()
    flash("Course removed.", "courses")
    return redirect(url_for("add_courses"))


# ---------- CREATE GROUP ----------
@app.route("/create_group", methods=["GET", "POST"])
@login_required
def create_group():
    email = session["email"]
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == "POST":
        course_id = request.form.get("course_id")
        group_name = request.form.get("group_name")
        day = request.form.get("day")
        start = request.form.get("start")
        end = request.form.get("end")
        mode = request.form.get("mode")
        location = request.form.get("location")
        max_size = request.form.get("max_size")

        cur.execute("SELECT MAX(SUBSTR(group_id, 2)) AS max_id FROM StudyGroups")
        result = cur.fetchone()["max_id"]
        next_num = (int(result) if result else 0) + 1
        group_id = f"G{next_num:03d}"

        cur.execute("""
            INSERT INTO StudyGroups
              (group_id, course_id, group_name, meeting_day, start_time, end_time,
               meeting_mode, max_size, location)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (group_id, course_id, group_name, day, start, end, mode, max_size, location))

        cur.execute(
            "INSERT INTO GroupMembers (group_id, email, role) VALUES (?, ?, 'leader')",
            (group_id, email),
        )

        conn.commit()
        flash("Study group created.", "groups")

    cur.execute("SELECT * FROM Courses ORDER BY subject, course_number")
    courses = cur.fetchall()
    conn.close()

    return render_template("create_group.html", courses=courses)


# ---------- SEARCH GROUPS ----------
@app.route("/search_groups")
@login_required
def search_groups():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM Courses ORDER BY subject, course_number")
    courses = cur.fetchall()

    course_id = request.args.get("course_id", "").strip()
    params = []
    sql = """
        SELECT g.group_id, g.group_name, g.meeting_day, g.start_time, g.end_time,
               g.meeting_mode, c.subject, c.course_number
        FROM StudyGroups g
        JOIN Courses c ON g.course_id = c.course_id
        WHERE 1=1
    """

    if course_id:
        sql += " AND g.course_id = ?"
        params.append(course_id)

    cur.execute(sql, params)
    groups = cur.fetchall()
    conn.close()

    return render_template("search_groups.html", courses=courses, groups=groups)


@app.route("/join_group/<group_id>")
@login_required
def join_group(group_id):
    email = session["email"]
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT 1 FROM GroupMembers WHERE group_id = ? AND email = ?",
        (group_id, email),
    )
    if cur.fetchone():
        flash("Already in group.", "groups")
        conn.close()
        return redirect(url_for("search_groups"))

    cur.execute("""
        SELECT max_size,
               (SELECT COUNT(*) FROM GroupMembers WHERE group_id = ?) AS member_count
        FROM StudyGroups
        WHERE group_id = ?
    """, (group_id, group_id))

    row = cur.fetchone()
    if row["member_count"] >= row["max_size"]:
        flash("Group is full.", "groups")
        conn.close()
        return redirect(url_for("search_groups"))

    cur.execute(
        "INSERT INTO GroupMembers (group_id, email, role) VALUES (?, ?, 'member')",
        (group_id, email),
    )
    conn.commit()
    conn.close()
    flash("Joined group.", "groups")
    return redirect(url_for("search_groups"))


# ---------- MY GROUPS ----------
@app.route("/my_groups")
@login_required
def my_groups():
    email = session["email"]
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT g.group_id,g.group_name, c.subject, c.course_number,
               g.meeting_day, g.start_time, g.end_time,
               gm.role
        FROM GroupMembers gm
        JOIN StudyGroups g ON gm.group_id = g.group_id
        JOIN Courses c ON g.course_id = c.course_id
        WHERE gm.email = ?
        ORDER BY c.subject, c.course_number
    """, (email,))
    groups = cur.fetchall()
    conn.close()

    return render_template("my_groups.html", groups=groups)

@app.route("/leave_group", methods=["POST"])
@login_required
def leave_group():
    email = session["email"]
    group_id = request.form.get("group_id")

    conn = get_db_connection()
    cur = conn.cursor()

    # Check if user is leader
    cur.execute("""
        SELECT role FROM GroupMembers
        WHERE group_id = ? AND email = ?
    """, (group_id, email))
    row = cur.fetchone()

    if not row:
        flash("You are not a member of this group.", "groups")
        conn.close()
        return redirect(url_for("my_groups"))

    role = row["role"]

    # Optional: block leaders from leaving their own group
    if role == "leader":
        flash("Leaders cannot leave their own group.", "groups")
        conn.close()
        return redirect(url_for("my_groups"))

    # Remove from group
    cur.execute("""
        DELETE FROM GroupMembers
        WHERE group_id = ? AND email = ?
    """, (group_id, email))
    conn.commit()
    conn.close()

    flash("You left the group.", "groups")
    return redirect(url_for("my_groups"))

@app.route("/delete_group", methods=["POST"])
@login_required
def delete_group():
    email = session["email"]
    group_id = request.form.get("group_id")

    conn = get_db_connection()
    cur = conn.cursor()

    # Check user role in that group
    cur.execute("""
        SELECT role FROM GroupMembers
        WHERE group_id = ? AND email = ?
    """, (group_id, email))
    row = cur.fetchone()

    # Optional: allow admin to delete any group
    is_admin = (email == "admin@studysync.com")

    if not row and not is_admin:
        flash("You are not allowed to delete this group.", "groups")
        conn.close()
        return redirect(url_for("my_groups"))

    role = row["role"] if row else None

    # if role != "leader" and not is_admin:
    #     flash("Only the group leader or an admin can delete this group.")
    #     conn.close()
    #     return redirect(url_for("my_groups"))

    if not is_admin and role != "leader":
        flash("Only the group leader or an admin can delete this group.", "groups")
        conn.close()
        return redirect(url_for("my_groups"))
    
    # Delete all members
    cur.execute("DELETE FROM GroupMembers WHERE group_id = ?", (group_id,))

    # Delete the group itself
    cur.execute("DELETE FROM StudyGroups WHERE group_id = ?", (group_id,))
    conn.commit()
    conn.close()

    flash("Group deleted successfully.", "groups")
    return redirect(url_for("my_groups"))

@app.route("/admin")
@login_required
def admin():
    # ensure current user is admin
    if session["email"] != "admin@studysync.com":
        flash("Admins only.", "auth")
        return redirect(url_for("index"))

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM Students")
    students = cur.fetchall()

    cur.execute("SELECT * FROM Courses")
    courses = cur.fetchall()

    # join groups with course info + member count
    cur.execute("""
        SELECT g.group_id, g.group_name, g.meeting_day, 
               g.start_time, g.end_time, g.meeting_mode,
               g.max_size,
               c.subject, c.course_number,
               (SELECT COUNT(*) FROM GroupMembers gm WHERE gm.group_id = g.group_id) AS member_count
        FROM StudyGroups g
        JOIN Courses c ON g.course_id = c.course_id
    """)
    groups = cur.fetchall()

    cur.execute("SELECT * FROM GroupMembers")
    members = cur.fetchall()

    conn.close()

    return render_template("admin.html",
                           students=students,
                           courses=courses,
                           groups=groups,
                           members=members)

# ---------- EXPLORE USERS ----------
@app.route("/explore_users")
@login_required
def explore_users():
    conn = get_db_connection()
    cur = conn.cursor()

    # Get all students
    cur.execute("SELECT * FROM Students ORDER BY first_name, last_name")
    students = cur.fetchall()

    # For each student, get their availabilities and courses
    users = []
    for student in students:
        email = student["email"]
        # Get availabilities
        cur.execute("""
            SELECT day_of_week, start_time, end_time
            FROM Availability
            WHERE email = ?
            ORDER BY day_of_week, start_time
        """, (email,))
        availabilities = cur.fetchall()
        # Get courses
        cur.execute("""
            SELECT c.course_id, c.subject, c.course_number, c.title
            FROM Enrollments e
            JOIN Courses c ON e.course_id = c.course_id
            WHERE e.email = ?
            ORDER BY c.subject, c.course_number
        """, (email,))
        courses = cur.fetchall()
        user = {
            "email": student["email"],
            "first_name": student["first_name"],
            "last_name": student["last_name"],
            "major": student["major"],
            "class_year": student["class_year"],
            "preferred_mode": student["preferred_mode"],
            "availabilities": availabilities,
            "courses": courses
        }
        users.append(user)
    conn.close()
    return render_template("explore_users.html", users=users)

if __name__ == "__main__":
    app.run(debug=True)
