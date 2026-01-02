🏗️ Tomide Construction Group (TCG)

A full-stack Construction Management & Service Request Platform built with Flask, designed to handle customer quote requests, staff assignments, and internal workflow management through dedicated Admin and Staff dashboards.

🚀 Project Overview

TCG allows customers to request construction-related services while enabling administrators and staff to manage, assign, and complete those requests efficiently.

Important:
The core business logic and features of this application live inside the Admin and Staff portals, not the public-facing pages.

Access to these portals is intentionally hidden from the main UI and is linked via the footer for internal users only.

🔑 Admin & Staff Portal Access

The Admin / Staff Login link is located in the footer of the website.

Admin Demo Credentials
Username: admintcg
Password: 219369


⚠️ These credentials are for demo/review purposes only.

🧩 Key Functionalities
👨‍💼 Admin Dashboard

View all quote requests and contact requests

Assign quote requests to staff members

Track request status:

Assigned

Pending

Completed

Monitor staff activity and workload

Centralized management of customer interactions

👷 Staff Dashboard

View only requests assigned to the logged-in staff

Requests appear as:

Pending (when newly assigned)

Completed (after work is done)

Notification badges for unattended requests

Clean task-based workflow for productivity

🧑‍💻 Customer Features

Submit quote requests from the public website

Submit contact messages

No login required for customers

🛠️ Tech Stack

Backend: Flask (Python)

Frontend: HTML, Bootstrap 5, Jinja2

Database: MySQL (SQLAlchemy ORM)

Authentication: Session-based login

Email Service: Configurable via environment variables

Version Control: Git & GitHub

🔐 Environment Configuration

Sensitive data (email credentials, database URIs, API keys) are stored using environment variables and excluded from version control via .gitignore.

Create a .env file locally to run the project.

📦 Installation (Local Setup)
git clone https://github.com/Mxxxly/tomideconstructiongroup.git
cd tomideconstructiongroup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
flask run

📌 Notes for Reviewers

Admin and staff features are not public-facing

Portal access is intentionally subtle to simulate a real internal system

Workflow mirrors real-world task assignment and completion logic

📄 License

This project is for portfolio and learning purposes.