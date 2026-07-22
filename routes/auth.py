from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import User
from extensions import db
from datetime import datetime

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        if not email or not password:
            flash('Please fill in all fields', 'error')
            return render_template('login.html')
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            # update last active timestamp
            user.last_active = datetime.utcnow()
            db.session.commit()
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard.dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        # basic validation
        if not username or not email or not password:
            flash('All fields are required', 'error')
            return render_template('signup.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters', 'error')
            return render_template('signup.html')
        
        # check if user exists already
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return render_template('signup.html')
        
        if User.query.filter_by(username=username).first():
            flash('Username taken', 'error')
            return render_template('signup.html')
        
        try:
            new_user = User(
                username=username,
                email=email,
                password_hash=generate_password_hash(password),
                role='member'  # new users are always members
            )
            db.session.add(new_user)
            db.session.commit()
            
            flash('Account created! Please login.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('Something went wrong, try again', 'error')
            print(f"Signup error: {e}")
    
    return render_template('signup.html')

@auth_bp.route('/logout')
@login_required
def logout():
    db.session.rollback()
    logout_user()
    flash('Logged out', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/demo-login', methods=['POST'])
def demo_login():
    demo_user = User.query.filter_by(email="demo@taskpulse.com").first()
    if not demo_user:
        try:
            # Create Demo Admin
            demo_user = User(
                username="DemoAdmin",
                email="demo@taskpulse.com",
                password_hash=generate_password_hash("demo123"),
                role='admin'
            )
            db.session.add(demo_user)
            db.session.commit()
            
            # Create Bob and Alice members
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
            
            # Create Project
            from models import Project, Task, TaskComment, TimeLog, Notification
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
            
            # Create Tasks
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
            
            # Create Time Logs
            from datetime import timedelta
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
            
            # Create Comments
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
            
            # Create Notifications
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
            
        except Exception as e:
            db.session.rollback()
            flash("Could not create demo user or dummy data", "error")
            print(f"Demo seed error: {e}")
            return redirect(url_for('auth.login'))
            
    login_user(demo_user)
    flash('Logged in as Demo Admin with sample data!', 'success')
    return redirect(url_for('dashboard.dashboard'))

@auth_bp.before_app_request
def update_last_active():
    """Update last_active timestamp on every request for logged-in users, throttled to 5 minutes"""
    if current_user.is_authenticated:
        try:
            if not current_user.last_active or (datetime.utcnow() - current_user.last_active).total_seconds() > 300:
                current_user.last_active = datetime.utcnow()
                db.session.commit()
        except:
            db.session.rollback()
