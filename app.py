from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import random
from datetime import datetime

app = Flask(__name__)
app.secret_key = "employee_crm_secret"

DATABASE = "database/employee_crm.db"


# ==============================
# DATABASE CONNECTION
# ==============================

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# ==============================
# INITIALIZE DATABASE
# ==============================

def init_db():

    conn = get_db_connection()

    with open("database/schema.sql", "r") as f:
        conn.executescript(f.read())

    # Create default admin if not exists

    admin = conn.execute(
        "SELECT * FROM admins WHERE email=?",
        ("admin@gmail.com",)
    ).fetchone()

    if admin is None:

        conn.execute(
            """
            INSERT INTO admins
            (name,email,password)
            VALUES
            (?,?,?)
            """,
            (
                "Administrator",
                "admin@gmail.com",
                "admin123"
            )
        )

        conn.commit()

    conn.close()


init_db()
# ==============================
# INITIALIZE DATABASE
# ==============================
# ==============================
# GENERATE COMPLAINT ID
# ==============================

def generate_ref():

    year = datetime.now().year

    number = random.randint(1000,9999)

    return f"CMP{year}{number}"


# ==============================
# LOGIN REQUIRED
# ==============================

def employee_logged_in():

    return "employee_id" in session


def admin_logged_in():

    return "admin_id" in session


# ==============================
# HOME
# ==============================

@app.route("/")

def index():

    return render_template("index.html")


# ==============================
# REGISTER
# ==============================

@app.route("/register",methods=["GET","POST"])

def register():

    if request.method=="POST":

        name=request.form["name"]

        email=request.form["email"]

        phone=request.form["phone"]

        department=request.form["department"]

        designation=request.form["designation"]

        password=request.form["password"]

        conn=get_db_connection()

        employee=conn.execute(
            "SELECT * FROM employees WHERE email=?",
            (email,)
        ).fetchone()

        if employee:

            flash("Email already exists","danger")

            conn.close()

            return redirect(url_for("register"))

        conn.execute(
            """
            INSERT INTO employees
            (name,email,phone,department,designation,password)
            VALUES
            (?,?,?,?,?,?)
            """,
            (
                name,
                email,
                phone,
                department,
                designation,
                password
            )
        )

        conn.commit()

        conn.close()

        flash("Registration Successful","success")

        return redirect(url_for("login"))

    return render_template("register.html")
# ==============================
# EMPLOYEE LOGIN
# ==============================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()

        employee = conn.execute(
            """
            SELECT * FROM employees
            WHERE email=? AND password=?
            """,
            (email, password)
        ).fetchone()

        conn.close()

        if employee:

            session.clear()

            session["employee_id"] = employee["employee_id"]
            session["name"] = employee["name"]

            flash("Welcome Back!", "success")

            return redirect(url_for("employee_dashboard"))

        flash("Invalid Email or Password", "danger")

    return render_template("login.html")


# ==============================
# LOGOUT
# ==============================

@app.route("/logout")
def logout():

    session.clear()

    flash("Logged out successfully.", "success")

    return redirect(url_for("login"))


# ==============================
# EMPLOYEE DASHBOARD
# ==============================

@app.route("/employee_dashboard")
def employee_dashboard():

    if not employee_logged_in():
        return redirect(url_for("login"))

    employee_id = session["employee_id"]

    conn = get_db_connection()

    employee = conn.execute(
        """
        SELECT * FROM employees
        WHERE employee_id=?
        """,
        (employee_id,)
    ).fetchone()

    total = conn.execute(
        """
        SELECT COUNT(*) AS count
        FROM complaints
        WHERE employee_id=?
        """,
        (employee_id,)
    ).fetchone()["count"]

    pending = conn.execute(
        """
        SELECT COUNT(*) AS count
        FROM complaints
        WHERE employee_id=?
        AND status='Pending'
        """,
        (employee_id,)
    ).fetchone()["count"]

    in_progress = conn.execute(
        """
        SELECT COUNT(*) AS count
        FROM complaints
        WHERE employee_id=?
        AND status='In Progress'
        """,
        (employee_id,)
    ).fetchone()["count"]

    resolved_closed = conn.execute(
        """
        SELECT COUNT(*) AS count
        FROM complaints
        WHERE employee_id=?
        AND status IN ('Resolved','Closed')
        """,
        (employee_id,)
    ).fetchone()["count"]

    recent_complaints = conn.execute(
        """
        SELECT *
        FROM complaints
        WHERE employee_id=?
        ORDER BY date_submitted DESC
        LIMIT 5
        """,
        (employee_id,)
    ).fetchall()

    conn.close()

    stats = {
        "total": total,
        "pending": pending,
        "in_progress": in_progress,
        "resolved_closed": resolved_closed
    }

    return render_template(
        "employee_dashboard.html",
        employee=employee,
        stats=stats,
        recent_complaints=recent_complaints
    )
# ==============================
# SUBMIT COMPLAINT
# ==============================

@app.route("/submit_complaint", methods=["GET", "POST"])
def submit_complaint():

    if not employee_logged_in():
        return redirect(url_for("login"))

    if request.method == "POST":

        employee_id = session["employee_id"]

        title = request.form["title"]
        description = request.form["description"]
        category = request.form["category"]
        priority = request.form["priority"]

        complaint_ref = generate_ref()

        conn = get_db_connection()

        while conn.execute(
            "SELECT id FROM complaints WHERE complaint_ref=?",
            (complaint_ref,)
        ).fetchone():

            complaint_ref = generate_ref()

        conn.execute(
            """
            INSERT INTO complaints
            (
                complaint_ref,
                employee_id,
                title,
                description,
                category,
                priority,
                status
            )
            VALUES
            (?,?,?,?,?,?,?)
            """,
            (
                complaint_ref,
                employee_id,
                title,
                description,
                category,
                priority,
                "Pending"
            )
        )

        conn.commit()
        conn.close()

        flash(
            f"Complaint submitted successfully! Reference ID: {complaint_ref}",
            "success"
        )

        return redirect(url_for("employee_dashboard"))

    return render_template("submit_complaint.html")


# ==============================
# COMPLAINT HISTORY
# ==============================

@app.route("/complaint_history")
def complaint_history():

    if not employee_logged_in():
        return redirect(url_for("login"))

    employee_id = session["employee_id"]

    search = request.args.get("search", "").strip()
    category = request.args.get("category", "").strip()
    status = request.args.get("status", "").strip()
    priority = request.args.get("priority", "").strip()

    query = """
        SELECT *
        FROM complaints
        WHERE employee_id=?
    """

    values = [employee_id]

    if search:
        query += """
        AND (
            complaint_ref LIKE ?
            OR title LIKE ?
        )
        """
        values.extend([
            f"%{search}%",
            f"%{search}%"
        ])

    if category:
        query += " AND category=? "
        values.append(category)

    if status:
        query += " AND status=? "
        values.append(status)

    if priority:
        query += " AND priority=? "
        values.append(priority)

    query += " ORDER BY date_submitted DESC"

    conn = get_db_connection()

    complaints = conn.execute(
        query,
        values
    ).fetchall()

    conn.close()

    filters = {
        "search": search,
        "category": category,
        "status": status,
        "priority": priority
    }

    return render_template(
        "complaint_history.html",
        complaints=complaints,
        filters=filters
    )
# ==============================
# PROFILE
# ==============================

@app.route("/profile", methods=["GET", "POST"])
def profile():

    if not employee_logged_in():
        return redirect(url_for("login"))

    employee_id = session["employee_id"]

    conn = get_db_connection()

    if request.method == "POST":

        name = request.form["name"]
        phone = request.form["phone"]
        department = request.form["department"]
        designation = request.form["designation"]

        conn.execute(
            """
            UPDATE employees
            SET
                name=?,
                phone=?,
                department=?,
                designation=?
            WHERE employee_id=?
            """,
            (
                name,
                phone,
                department,
                designation,
                employee_id
            )
        )

        conn.commit()

        session["name"] = name

        flash("Profile updated successfully.", "success")

    employee = conn.execute(
        """
        SELECT *
        FROM employees
        WHERE employee_id=?
        """,
        (employee_id,)
    ).fetchone()

    conn.close()

    return render_template(
        "profile.html",
        employee=employee
    )


# ==============================
# ADMIN LOGIN
# ==============================

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()

        admin = conn.execute(
            """
            SELECT *
            FROM admins
            WHERE email=? AND password=?
            """,
            (email, password)
        ).fetchone()

        conn.close()

        if admin:

            session.clear()

            session["admin_id"] = admin["admin_id"]
            session["name"] = admin["name"]

            flash("Admin Login Successful", "success")

            return redirect(url_for("admin_dashboard"))

        flash("Invalid Admin Credentials", "danger")

    return render_template("admin_login.html")
# ==============================
# ADMIN DASHBOARD
# ==============================

@app.route("/admin/dashboard")
def admin_dashboard():

    if not admin_logged_in():
        return redirect(url_for("admin_login"))

    conn = get_db_connection()

    complaints = conn.execute(
        """
        SELECT
            complaints.*,
            employees.name
        FROM complaints
        JOIN employees
        ON complaints.employee_id = employees.employee_id
        ORDER BY complaints.date_submitted DESC
        """
    ).fetchall()

    total_complaints = conn.execute(
        "SELECT COUNT(*) AS total FROM complaints"
    ).fetchone()["total"]

    total_employees = conn.execute(
        "SELECT COUNT(*) AS total FROM employees"
    ).fetchone()["total"]

    pending = conn.execute(
        """
        SELECT COUNT(*) AS total
        FROM complaints
        WHERE status='Pending'
        """
    ).fetchone()["total"]

    in_progress = conn.execute(
        """
        SELECT COUNT(*) AS total
        FROM complaints
        WHERE status='In Progress'
        """
    ).fetchone()["total"]

    resolved = conn.execute(
        """
        SELECT COUNT(*) AS total
        FROM complaints
        WHERE status='Resolved'
        """
    ).fetchone()["total"]

    closed = conn.execute(
        """
        SELECT COUNT(*) AS total
        FROM complaints
        WHERE status='Closed'
        """
    ).fetchone()["total"]

    conn.close()

    stats = {
        "employees": total_employees,
        "complaints": total_complaints,
        "pending": pending,
        "in_progress": in_progress,
        "resolved": resolved,
        "closed": closed
    }

    return render_template(
        "admin_dashboard.html",
        complaints=complaints,
        stats=stats
    )


# ==============================
# ADMIN EMPLOYEES
# ==============================

@app.route("/admin/employees")
def admin_employees():

    if not admin_logged_in():
        return redirect(url_for("admin_login"))

    conn = get_db_connection()

    employees = conn.execute(
        """
        SELECT *
        FROM employees
        ORDER BY employee_id DESC
        """
    ).fetchall()

    conn.close()

    return render_template(
        "admin_employees.html",
        employees=employees
    )


# ==============================
# ADMIN COMPLAINTS
# ==============================

@app.route("/admin/complaints")
def admin_complaints():

    if not admin_logged_in():
        return redirect(url_for("admin_login"))

    conn = get_db_connection()

    complaints = conn.execute(
        """
        SELECT
            complaints.*,
            employees.name
        FROM complaints
        JOIN employees
        ON complaints.employee_id = employees.employee_id
        ORDER BY complaints.date_submitted DESC
        """
    ).fetchall()

    conn.close()

    return render_template(
        "admin_dashboard.html",
        complaints=complaints
    )
# ==============================
# UPDATE COMPLAINT STATUS
# ==============================

@app.route("/admin/update_status/<int:id>", methods=["POST"])
def update_status(id):

    if not admin_logged_in():
        return redirect(url_for("admin_login"))

    status = request.form["status"]

    conn = get_db_connection()

    conn.execute(
        """
        UPDATE complaints
        SET
            status=?,
            last_updated=CURRENT_TIMESTAMP
        WHERE id=?
        """,
        (
            status,
            id
        )
    )

    conn.commit()
    conn.close()

    flash("Complaint status updated successfully.", "success")

    return redirect(url_for("admin_dashboard"))


# ==============================
# DELETE COMPLAINT (OPTIONAL)
# ==============================

@app.route("/delete_complaint/<int:id>")
def delete_complaint(id):

    if not employee_logged_in():
        return redirect(url_for("login"))

    conn = get_db_connection()

    complaint = conn.execute(
        """
        SELECT *
        FROM complaints
        WHERE id=?
        """,
        (id,)
    ).fetchone()

    if complaint and complaint["employee_id"] == session["employee_id"]:

        conn.execute(
            """
            DELETE FROM complaints
            WHERE id=?
            """,
            (id,)
        )

        conn.commit()

        flash("Complaint deleted successfully.", "success")

    conn.close()

    return redirect(url_for("complaint_history"))


# ==============================
# ERROR HANDLERS
# ==============================

@app.errorhandler(404)
def page_not_found(error):
    return "<h2>404 - Page Not Found</h2>", 404


@app.errorhandler(500)
def internal_server(error):
    return "<h2>500 - Internal Server Error</h2>", 500


# ==============================
# RUN APPLICATION
# ==============================

if __name__ == "__main__":
    app.run(
        debug=True
    )