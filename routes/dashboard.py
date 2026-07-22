from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models import Task, Project
from extensions import db
from datetime import date

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    # get statistics using database-level queries instead of loading all objects
    if current_user.is_admin():
        total = db.session.query(db.func.count(Task.id)).scalar()
        completed = db.session.query(db.func.count(Task.id)).filter_by(status='completed').scalar()
        in_progress = db.session.query(db.func.count(Task.id)).filter_by(status='in_progress').scalar()
        pending = db.session.query(db.func.count(Task.id)).filter_by(status='pending').scalar()
        overdue = db.session.query(db.func.count(Task.id)).filter(Task.status != 'completed', Task.due_date < date.today()).scalar()
        projects = Project.query.all()
        recent_tasks = Task.query.order_by(Task.created_at.desc()).limit(5).all()
    else:
        total = db.session.query(db.func.count(Task.id)).filter_by(assigned_to=current_user.id).scalar()
        completed = db.session.query(db.func.count(Task.id)).filter_by(assigned_to=current_user.id, status='completed').scalar()
        in_progress = db.session.query(db.func.count(Task.id)).filter_by(assigned_to=current_user.id, status='in_progress').scalar()
        pending = db.session.query(db.func.count(Task.id)).filter_by(assigned_to=current_user.id, status='pending').scalar()
        overdue = db.session.query(db.func.count(Task.id)).filter(Task.assigned_to=current_user.id, Task.status != 'completed', Task.due_date < date.today()).scalar()
        projects = current_user.projects
        recent_tasks = Task.query.filter_by(assigned_to=current_user.id).order_by(Task.created_at.desc()).limit(5).all()
    
    return render_template('dashboard.html', 
        total=total,
        completed=completed,
        in_progress=in_progress,
        overdue=overdue,
        pending=pending,
        projects=projects,
        recent_tasks=recent_tasks
    )

@dashboard_bp.route('/notifications/read', methods=['POST'])
@login_required
def mark_notifications_read():
    from models import Notification
    notifications = Notification.query.filter_by(user_id=current_user.id, is_read=False).all()
    for notif in notifications:
        notif.is_read = True
    db.session.commit()
    return {'status': 'success'}
