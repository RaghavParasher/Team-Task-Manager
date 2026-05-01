from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models import Task, Project
from datetime import date

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    # get tasks based on role
    if current_user.is_admin():
        all_tasks = Task.query.all()
        projects = Project.query.all()
    else:
        all_tasks = Task.query.filter_by(assigned_to=current_user.id).all()
        projects = current_user.projects
    
    # calculate stats
    total = len(all_tasks)
    completed = len([t for t in all_tasks if t.status == 'completed'])
    in_progress = len([t for t in all_tasks if t.status == 'in_progress'])
    overdue = len([t for t in all_tasks if t.is_overdue()])
    pending = len([t for t in all_tasks if t.status == 'pending'])
    
    # recent tasks (last 5)
    recent_tasks = sorted(all_tasks, key=lambda t: t.created_at, reverse=True)[:5]
    
    return render_template('dashboard.html', 
        total=total,
        completed=completed,
        in_progress=in_progress,
        overdue=overdue,
        pending=pending,
        projects=projects,
        recent_tasks=recent_tasks
    )
