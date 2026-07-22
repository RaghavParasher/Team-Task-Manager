from flask import Flask, redirect, url_for, render_template_string
from extensions import db, login_manager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os

csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])

def create_app():
    app = Flask(__name__)
    
    # config stuff
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-this')
    
    # Check for DATABASE_URL first, then Vercel's POSTGRES_URL
    db_url = os.environ.get('DATABASE_URL') or os.environ.get('POSTGRES_URL')
    
    if db_url:
        if db_url.startswith('postgres://'):
            db_url = db_url.replace('postgres://', 'postgresql://', 1)
    else:
        # Vercel's file system is read-only except for the /tmp directory.
        # If no Postgres database is linked, we MUST use /tmp for SQLite to prevent crashes.
        db_url = 'sqlite:////tmp/taskpulse.db'
        
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['WTF_CSRF_ENABLED'] = False  # Set to True once CSRF tokens are added to all templates
    
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    migrate = Migrate(app, db)
    csrf.init_app(app)
    limiter.init_app(app)
    
    # import models so they get registered
    from models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # register blueprints
    from routes.auth import auth_bp
    from routes.projects import projects_bp
    from routes.tasks import tasks_bp
    from routes.dashboard import dashboard_bp
    from routes.settings import settings_bp
    from routes.team import team_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(team_bp)
    
    @app.route('/')
    def index():
        return redirect(url_for('dashboard.dashboard'))
    
    # --- Global Error Handlers ---
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template_string(ERROR_PAGE, code=404, message="Page Not Found",
            detail="The page you're looking for doesn't exist."), 404

    @app.errorhandler(500)
    def internal_error(e):
        db.session.rollback()
        return render_template_string(ERROR_PAGE, code=500, message="Internal Server Error",
            detail="Something went wrong on our end. Please try again."), 500

    @app.errorhandler(403)
    def forbidden(e):
        return render_template_string(ERROR_PAGE, code=403, message="Access Denied",
            detail="You don't have permission to access this page."), 403
    
    # create tables & run migrations
    with app.app_context():
        db.create_all()
        _auto_migrate(app)
        _create_default_admin(app)
    
    return app

# simple error page template
ERROR_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ code }} - TaskPulse</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin:0; padding:0; box-sizing:border-box; }
        body { font-family:'Inter',sans-serif; background:#F8FAFC; display:flex;
               justify-content:center; align-items:center; min-height:100vh; }
        .error-box { text-align:center; padding:3rem; }
        .error-code { font-size:6rem; font-weight:800; color:#4F46E5; line-height:1; }
        .error-msg { font-size:1.5rem; font-weight:700; color:#1E293B; margin:1rem 0 0.5rem; }
        .error-detail { color:#64748B; margin-bottom:2rem; }
        .error-btn { display:inline-block; padding:10px 24px; background:#4F46E5; color:white;
                     text-decoration:none; border-radius:8px; font-weight:600; }
        .error-btn:hover { background:#4338CA; }
    </style>
</head>
<body>
    <div class="error-box">
        <div class="error-code">{{ code }}</div>
        <div class="error-msg">{{ message }}</div>
        <p class="error-detail">{{ detail }}</p>
        <a href="/" class="error-btn">← Go to Dashboard</a>
    </div>
</body>
</html>
"""

def _auto_migrate(app):
    """Auto-add missing columns to existing SQLite tables."""
    import sqlite3
    
    db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    if not os.path.isabs(db_path):
        db_path = os.path.join(app.instance_path, db_path)
    
    if not os.path.exists(db_path):
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # --- Task table migrations ---
        cursor.execute("PRAGMA table_info(task)")
        task_cols = [row[1] for row in cursor.fetchall()]
        
        if 'priority' not in task_cols:
            print("[AUTO-MIGRATE] Adding 'priority' column to task table...")
            cursor.execute("ALTER TABLE task ADD COLUMN priority VARCHAR(20) DEFAULT 'medium'")
        
        # --- User table migrations ---
        cursor.execute("PRAGMA table_info(user)")
        user_cols = [row[1] for row in cursor.fetchall()]
        
        if 'last_active' not in user_cols:
            print("[AUTO-MIGRATE] Adding 'last_active' column to user table...")
            cursor.execute("ALTER TABLE user ADD COLUMN last_active DATETIME")
        
        if 'notify_email' not in user_cols:
            print("[AUTO-MIGRATE] Adding 'notify_email' column to user table...")
            cursor.execute("ALTER TABLE user ADD COLUMN notify_email BOOLEAN DEFAULT 1")
        
        if 'notify_tasks' not in user_cols:
            print("[AUTO-MIGRATE] Adding 'notify_tasks' column to user table...")
            cursor.execute("ALTER TABLE user ADD COLUMN notify_tasks BOOLEAN DEFAULT 1")
        
        # --- Fix old status values ---
        cursor.execute("UPDATE task SET status='pending' WHERE status='todo'")
        cursor.execute("UPDATE task SET status='completed' WHERE status='done'")
        
        conn.commit()
        print("[AUTO-MIGRATE] All migrations applied.")
        
    except Exception as e:
        print(f"[AUTO-MIGRATE] Warning: {e}")
    finally:
        conn.close()

def _create_default_admin(app):
    """create default admin and demo user accounts and seed mock data so the app is populated out of the box"""
    from models import User, Project, Task, TaskComment, TimeLog, Notification
    from werkzeug.security import generate_password_hash
    from datetime import datetime, timedelta
    
    # 1. Default Admin
    if not User.query.filter_by(email='admin@taskpulse.com').first():
        admin = User(
            username='admin',
            email='admin@taskpulse.com',
            password_hash=generate_password_hash('admin123'),
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
        print("Created default admin account")
        
    # 2. Demo Admin & Sample Data
    demo_user = User.query.filter_by(email='demo@taskpulse.com').first()
    if not demo_user:
        try:
            demo_user = User(
                username="DemoAdmin",
                email="demo@taskpulse.com",
                password_hash=generate_password_hash("demo123"),
                role='admin'
            )
            db.session.add(demo_user)
            db.session.commit()
            
            alice = User(
                username="Alice",
                email="alice@taskpulse.com",
                password_hash=generate_password_hash("member123"),
                role='member'
            )
            bob = User(
                username="Bob",
                email="bob@taskpulse.com",
                password_hash=generate_password_hash("member123"),
                role='member'
            )
            db.session.add_all([alice, bob])
            db.session.commit()
            
            # Project
            project = Project(
                name="✨ Website Redesign",
                description="Modernizing our landing page and developer dashboard with TaskPulse.",
                created_by=demo_user.id
            )
            project.members.append(demo_user)
            project.members.append(alice)
            project.members.append(bob)
            db.session.add(project)
            db.session.commit()
            
            # Tasks
            task1 = Task(
                title="Design modern homepage mockups",
                description="Create high-fidelity landing page designs in Figma matching the new branding.",
                status="completed",
                priority="high",
                project_id=project.id,
                assigned_to=alice.id
            )
            task2 = Task(
                title="Implement Auth and API endpoints",
                description="Write secure backend authentication handlers and hybrid REST APIs.",
                status="in_progress",
                priority="high",
                project_id=project.id,
                assigned_to=bob.id
            )
            task3 = Task(
                title="Setup database indexes & migrations",
                description="Add indices for foreign key attributes to speed up dashboard queries.",
                status="pending",
                priority="medium",
                project_id=project.id,
                assigned_to=demo_user.id
            )
            task4 = Task(
                title="Draft developer API documentation",
                description="Create clear markdown instructions detailing how to consume tasks endpoints.",
                status="pending",
                priority="low",
                project_id=project.id,
                assigned_to=alice.id
            )
            db.session.add_all([task1, task2, task3, task4])
            db.session.commit()
            
            # Time logs
            log1 = TimeLog(
                task_id=task1.id,
                user_id=alice.id,
                start_time=datetime.utcnow() - timedelta(hours=4),
                end_time=datetime.utcnow() - timedelta(hours=1),
                duration=10800
            )
            log2 = TimeLog(
                task_id=task2.id,
                user_id=bob.id,
                start_time=datetime.utcnow() - timedelta(hours=2),
                end_time=datetime.utcnow() - timedelta(minutes=30),
                duration=5400
            )
            db.session.add_all([log1, log2])
            
            # Comments
            comment1 = TaskComment(
                content="Homepage designs are completed! Shared Figma link in slack.",
                task_id=task1.id,
                user_id=alice.id
            )
            comment2 = TaskComment(
                content="Working on resolving Gunicorn worker session timeouts.",
                task_id=task2.id,
                user_id=bob.id
            )
            db.session.add_all([comment1, comment2])
            
            # Notifications
            notif1 = Notification(
                user_id=demo_user.id,
                message="Figma designs for 'Website Redesign' have been uploaded by Alice."
            )
            notif2 = Notification(
                user_id=demo_user.id,
                message="Bob started work on 'Implement Auth and API endpoints'."
            )
            db.session.add_all([notif1, notif2])
            
            db.session.commit()
            print("Successfully seeded all demo and dummy data on startup.")
        except Exception as e:
            db.session.rollback()
            print(f"Startup seeding failed: {e}")

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
