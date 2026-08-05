# 🚀 TaskPulse – Smart Work Management System

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Neon.tech-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://neon.tech/)
[![Vercel](https://img.shields.io/badge/Vercel-Deployed-000000?style=for-the-badge&logo=vercel&logoColor=white)](https://vercel.com/)
[![Chart.js](https://img.shields.io/badge/Chart.js-Interactive-FF6384?style=for-the-badge&logo=chartdotjs&logoColor=white)](https://www.chartjs.org/)

**TaskPulse** is a premium, responsive, role-based work management platform designed for teams to organize projects, assign tasks, log working hours, and track deliverables in real-time.

<br/>
<img src="./mockup.jpg" width="100%" alt="TaskPulse Dashboard Mockup" />
<br/>

---

## 🔗 Live Application & Demo Access

The project is fully deployed and connected to a persistent cloud database:

👉 **[Launch TaskPulse Live Demo](https://team-task-manager-26j1meovi-raghavparashers-projects.vercel.app/auth/login?next=%2Fdashboard)**

### ⚡ Recruiter / Fast Guest Access
No signup required! Use the single-click **Fast Demo Guest Login** button on the login page, or sign in manually with:
* **Email:** `demo@taskpulse.com`
* **Password:** `demo123`

---

## ✨ Features Breakdown

### 📋 1. Interactive Kanban Board & Lists
* Toggle seamlessly between a tabular **List View** and a modern **Kanban Board** grid.
* Move tasks between `Pending`, `In Progress`, and `Completed` columns using intuitive **HTML5 Drag-and-Drop**.
* Task cards display assignees, priority indicators (🔴 High, 🟡 Medium, 🟢 Low), and work progress metrics.

### ⏱️ 2. Integrated Time-Logger (Stopwatch)
* Start and stop working timers directly from inside the task detail modal.
* Automatically records work durations per member and aggregates total time logs in the project view.

### 💬 3. Team Collaboration (Comments)
* Leave notes, paste links, and discuss progress directly inside task detail feeds.
* Timestamped user initials allow team members to see who commented and when.

### 🔔 4. Live Notification Bells
* Displays real-time unread alert badges when you are assigned to a task or when project status updates.
* Quick dropdown panel in the navbar lets you view details and mark all notifications as read.

### 📊 5. Workload Analytics Dashboard
* View total tasks, completed ratio progress bars, and overdue task warnings instantly.
* Real-time doughnut charts powered by **Chart.js** visualize project task distribution.

### 🛡️ 6. Production-Grade Security & Performance
* Hardened session cookies and rate-limiting (`Flask-Limiter`) prevent brute-force attacks.
* CSRF token protection integrated globally.
* Optimized SQL counts on the database layer rather than loading heavy objects into Python memory.

---

## 📂 Project Architecture

```text
taskpulse/
├── app.py                 # App factory, db.create_all(), error handlers, & auto-migration
├── extensions.py          # Flask-SQLAlchemy & Flask-Login manager setup
├── models.py              # User, Project, Task, TimeLog, TaskComment, Notification schemas
├── requirements.txt       # Production dependencies
├── vercel.json            # Vercel Serverless routing configurations
├── Procfile               # Heroku/Render production execution script
├── routes/
│   ├── auth.py            # Session management, Presence tracking, & Demo login logic
│   ├── dashboard.py       # Metrics queries & notification actions
│   ├── projects.py        # Project CRUD & team member assignments
│   ├── tasks.py           # Task CRUD, stopwatch handlers, & Kanban API routes
│   ├── settings.py        # Profile updates, security details, & notifications toggles
│   └── team.py            # User management CRUD
├── templates/             # Premium responsive HTML5 templates
└── static/                # Vanilla CSS styling & Frontend JS animations
```

---

## 🛠️ Local Setup Instructions

### 1. Clone & Navigate
```bash
git clone https://github.com/RaghavParasher/Team-Task-Manager.git
cd Team-Task-Manager
```

### 2. Configure Environment
Create a `.env` file in the root directory (optional, defaults to SQLite local file if omitted):
```text
DATABASE_URL=postgresql://username:password@host:port/dbname
SECRET_KEY=your-custom-session-secret-key
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Launch Development Server
```bash
python app.py
```
Open **`http://127.0.0.1:5000`** in your browser and log in!

---

## 📄 License
This project is open-source and available for educational and recruitment reviews.

*Built with ❤️ using Flask & PostgreSQL | **TaskPulse***
