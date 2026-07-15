# 🛡️ ComplaintCRM — Employee Complaint Management System

A full-stack web application built with **Flask** and **SQLite** that gives organizations a centralized, transparent way to handle employee workplace complaints — from submission to resolution.

---

## 📌 Overview

Traditional workplace complaint handling (emails, verbal reports) is unorganized and hard to track. **ComplaintCRM** solves this by giving:

- **Employees** a portal to register, log in, submit complaints, and track their status in real time.
- **Admins** a dashboard to view all complaints, monitor statistics, and update complaint status.

---

## ✨ Features

### Employee Side
- Secure registration & login (session-based authentication)
- Submit complaints with category, priority, and description
- Auto-generated unique complaint reference ID (e.g. `CMP20261234`)
- View complaint history and live status tracking
- Profile management

### Admin Side
- Separate, secured admin login (not exposed on the public navbar)
- Dashboard with key stats — total employees, total complaints, pending/in-progress/resolved/closed counts
- View all complaints across employees with full details
- Update complaint status (Pending → In Progress → Resolved → Closed)
- Manage employee list

### Status Tracking
| Status | Meaning |
|---|---|
| 🟡 Pending | Complaint submitted, awaiting review |
| 🔵 In Progress | Admin is actively working on it |
| 🟢 Resolved | Issue has been resolved |
| ⚪ Closed | Complaint closed |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| Templating | Jinja2 |
| Database | SQLite |
| Frontend | HTML, CSS, Bootstrap |
| Auth | Flask session-based login |

---

## 📂 Project Structure

```
EmployeeComplaintCRM/
├── app.py                     # Main Flask application & routes
├── requirements.txt
├── database/
│   └── schema.sql             # DB schema (employees, complaints, admins)
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── register.html
│   ├── login.html
│   ├── employee_dashboard.html
│   ├── submit_complaint.html
│   ├── complaint_history.html
│   ├── complaint_details.html
│   ├── profile.html
│   ├── admin_login.html
│   └── admin_dashboard.html
└── static/
    ├── css/
    └── js/
```

---

## ⚙️ Setup & Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/EmployeeComplaintCRM.git
   cd EmployeeComplaintCRM
   ```

2. **Create a virtual environment (optional but recommended)**
   ```bash
   python -m venv venv
   venv\Scripts\activate      # Windows
   source venv/bin/activate   # macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the app**
   ```bash
   python app.py
   ```

5. Open your browser at:
   ```
   http://127.0.0.1:5000
   ```

---

## 🔑 Default Admin Access

Admin login is intentionally not linked on the public navbar (role-based access separation). Access it directly at:

```
http://127.0.0.1:5000/admin/login
```

> Default admin credentials are seeded in the database for demo purposes — update them before any real deployment.

---

## 🚀 Future Improvements

- Hash passwords using Werkzeug's `generate_password_hash` instead of plain text
- Email notifications on complaint status change
- Pagination for large complaint lists
- Role-based access decorators instead of manual session checks

---

## 👤 Author

Built as a personal project to explore full-stack development with Flask.
