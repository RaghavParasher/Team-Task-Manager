# 🚀 Ethara.ai – Smart Work Management System

A clean, role-based team task management web application built with **Flask** and **SQLAlchemy**. Designed for small teams to manage projects, assign tasks, and track progress.

---

## ✨ Features

### 🔐 Authentication & Roles
- Login / Signup with password hashing
- **Admin** – Full access: create projects, assign tasks, manage team
- **Member** – View all projects, update assigned tasks, view team

### 📊 Dashboard
- Real-time stats: Total Tasks, Completed, In Progress, Overdue
- Visual progress bar (% completed)
- Project-wise task distribution chart
- Recent tasks with priority badges

### 📁 Project Management
- Create, view, and delete projects
- Add/remove team members per project
- Members can view all projects (read-only for unassigned)

### 📋 Task Management
- Create tasks with title, description, priority, due date
- Assign tasks to team members
- Status tracking: Pending → In Progress → Completed
- Priority levels: 🔴 High, 🟡 Medium, 🟢 Low
- Overdue detection

### 👥 Team Management
- View all team members with role badges and activity status
- Admin can add/remove members
- User avatar initials

### ⚙️ Settings
- **Profile** – Update username and email
- **Security** – Change password with validation
- **Notifications** – Toggle email and task update preferences

### 🎨 UI/UX
- Modern, minimal design with Inter font
- Indigo (#4F46E5) color palette
- Toast notifications (auto-dismiss)
- Smooth hover animations and transitions
- Fully responsive layout

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, Flask |
| Database | SQLite + SQLAlchemy |
| Frontend | HTML, CSS, JavaScript |
| Auth | Flask-Login, Werkzeug |
| Font | Google Fonts (Inter) |

---

## 📂 Project Structure

```
ethara/
├── app.py                 # App factory, error handlers, auto-migration
├── extensions.py          # SQLAlchemy & LoginManager init
├── models.py              # User, Project, Task models
├── requirements.txt       # Python dependencies
├── routes/
│   ├── auth.py            # Login, signup, logout
│   ├── dashboard.py       # Dashboard stats & charts
│   ├── projects.py        # Project CRUD
│   ├── tasks.py           # Task CRUD & status updates
│   ├── settings.py        # Profile, security, notifications
│   └── team.py            # Team management
├── templates/
│   ├── base.html          # Layout with navbar & toasts
│   ├── login.html         # Login page
│   ├── signup.html         # Signup page
│   ├── dashboard.html     # Dashboard with stats
│   ├── projects.html      # Projects listing
│   ├── view_project.html  # Single project view
│   ├── create_project.html
│   ├── tasks.html         # Tasks listing
│   ├── create_task.html   # Task creation form
│   ├── team.html          # Team members page
│   └── settings.html      # Settings page
└── static/
    ├── style.css          # All styles
    └── app.js             # Toast & animation logic
```

---

## 🚀 Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/harshkr04/Team-Tracker.git
cd Team-Tracker
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the application
```bash
python app.py
```

### 4. Open in browser
```
http://127.0.0.1:5000
```

---

## 📸 Screenshots

> Screenshots can be added after running the app locally.

---

## 📄 License

This project is for educational purposes.

---

Built with ❤️ using Flask | **Ethara.ai**
