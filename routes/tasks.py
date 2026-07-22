from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from models import Task, Project, User, TaskComment, TimeLog, Notification
from extensions import db
from datetime import datetime

tasks_bp = Blueprint('tasks', __name__, url_prefix='/tasks')

@tasks_bp.route('/')
@login_required
def list_tasks():
    """show all tasks - admins see everything, members see their own"""
    if current_user.is_admin():
        tasks = Task.query.all()
    else:
        tasks = Task.query.filter_by(assigned_to=current_user.id).all()
    
    # Calculate formatted total duration for each task
    durations = {}
    active_timers = {}
    for task in tasks:
        logs = TimeLog.query.filter_by(task_id=task.id).all()
        total_seconds = sum(l.duration for l in logs if l.duration)
        hours, remainder = divmod(total_seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        durations[task.id] = f"{hours}h {minutes}m"
        
        # Check if current user has active timer on this task
        active_log = TimeLog.query.filter_by(task_id=task.id, user_id=current_user.id, end_time=None).first()
        active_timers[task.id] = True if active_log else False
        
    return render_template('tasks.html', tasks=tasks, durations=durations, active_timers=active_timers)

@tasks_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_task():
    if not current_user.is_admin():
        flash('Only admins can create tasks', 'error')
        return redirect(url_for('tasks.list_tasks'))
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        project_id = request.form.get('project_id')
        assigned_to = request.form.get('assigned_to')
        priority = request.form.get('priority', 'medium')
        due_date_str = request.form.get('due_date', '')
        
        # validation
        if not title:
            flash('Task title is required', 'error')
            return redirect(url_for('tasks.create_task'))
        
        if not project_id:
            flash('Please select a project', 'error')
            return redirect(url_for('tasks.create_task'))
        
        # parse due date
        due_date = None
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid date format', 'error')
                return redirect(url_for('tasks.create_task'))
        
        try:
            task = Task(
                title=title,
                description=description,
                project_id=int(project_id),
                assigned_to=int(assigned_to) if assigned_to else None,
                due_date=due_date,
                status='pending',
                priority=priority
            )
            db.session.add(task)
            
            # Send notification to assigned user
            if assigned_to:
                notif = Notification(
                    user_id=int(assigned_to),
                    message=f"New task assigned to you: '{title}'"
                )
                db.session.add(notif)
                
            db.session.commit()
            
            flash('Task created!', 'success')
            return redirect(url_for('projects.view_project', project_id=project_id))
        except Exception as e:
            db.session.rollback()
            flash('Error creating task', 'error')
            print(f"Task create error: {e}")
            return redirect(url_for('tasks.create_task'))
    
    # GET - show form
    projects = Project.query.all()
    users = User.query.all()
    
    # check if project_id was passed as query param
    preselected_project = request.args.get('project_id')
    
    return render_template('create_task.html', projects=projects, users=users, preselected_project=preselected_project)

@tasks_bp.route('/<int:task_id>/update-status', methods=['POST'])
@login_required
def update_status(task_id):
    task = Task.query.get_or_404(task_id)
    
    # members can only update their own tasks
    if not current_user.is_admin() and task.assigned_to != current_user.id:
        if request.headers.get('Accept') == 'application/json' or request.is_json:
            return {'status': 'error', 'message': 'You can only update your own tasks'}, 403
        flash('You can only update your own tasks', 'error')
        return redirect(url_for('tasks.list_tasks'))
    
    # Support form-urlencoded and JSON requests
    if request.is_json:
        data = request.get_json()
        new_status = data.get('status')
    else:
        new_status = request.form.get('status')
    
    if new_status not in ['pending', 'in_progress', 'completed']:
        if request.headers.get('Accept') == 'application/json' or request.is_json:
            return {'status': 'error', 'message': 'Invalid status'}, 400
        flash('Invalid status', 'error')
        return redirect(url_for('tasks.list_tasks'))
    
    old_status = task.status
    task.status = new_status
    
    # Notification logic when task is completed
    if new_status == 'completed' and old_status != 'completed':
        proj = Project.query.get(task.project_id)
        if proj and proj.created_by != current_user.id:
            notif = Notification(
                user_id=proj.created_by,
                message=f"Task '{task.title}' was completed by {current_user.username}"
            )
            db.session.add(notif)
            
    db.session.commit()
    
    if request.headers.get('Accept') == 'application/json' or request.is_json:
        return {
            'status': 'success',
            'task_id': task.id,
            'new_status': task.status,
            'display': task.status_display()
        }
        
    flash('Task status updated!', 'success')
    next_url = request.form.get('next', url_for('tasks.list_tasks'))
    return redirect(next_url)

@tasks_bp.route('/<int:task_id>/comment', methods=['POST'])
@login_required
def add_comment(task_id):
    task = Task.query.get_or_404(task_id)
    content = request.form.get('content', '').strip()
    
    if not content:
        flash('Comment cannot be empty', 'error')
        return redirect(request.referrer or url_for('tasks.list_tasks'))
        
    comment = TaskComment(
        content=content,
        task_id=task.id,
        user_id=current_user.id
    )
    db.session.add(comment)
    db.session.commit()
    flash('Comment added!', 'success')
    return redirect(request.referrer or url_for('tasks.list_tasks'))

@tasks_bp.route('/<int:task_id>/time/start', methods=['POST'])
@login_required
def start_time(task_id):
    task = Task.query.get_or_404(task_id)
    active_log = TimeLog.query.filter_by(task_id=task.id, user_id=current_user.id, end_time=None).first()
    if active_log:
        return {'status': 'error', 'message': 'Timer already running'}, 400
        
    log = TimeLog(
        task_id=task.id,
        user_id=current_user.id,
        start_time=datetime.utcnow()
    )
    db.session.add(log)
    db.session.commit()
    return {'status': 'success', 'message': 'Timer started'}

@tasks_bp.route('/<int:task_id>/time/stop', methods=['POST'])
@login_required
def stop_time(task_id):
    task = Task.query.get_or_404(task_id)
    active_log = TimeLog.query.filter_by(task_id=task.id, user_id=current_user.id, end_time=None).first()
    if not active_log:
        return {'status': 'error', 'message': 'No running timer found'}, 400
        
    active_log.end_time = datetime.utcnow()
    duration_delta = active_log.end_time - active_log.start_time
    active_log.duration = int(duration_delta.total_seconds())
    db.session.commit()
    
    # Calculate formatted total duration
    total_seconds = sum(l.duration for l in TimeLog.query.filter_by(task_id=task.id).all() if l.duration)
    hours, remainder = divmod(total_seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    formatted_duration = f"{hours}h {minutes}m"
    
    return {
        'status': 'success', 
        'message': 'Timer stopped', 
        'duration': active_log.duration, 
        'formatted_total': formatted_duration
    }

@tasks_bp.route('/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    if not current_user.is_admin():
        flash('Only admins can delete tasks', 'error')
        return redirect(url_for('tasks.list_tasks'))
    
    task = Task.query.get_or_404(task_id)
    proj_id = task.project_id
    
    try:
        db.session.delete(task)
        db.session.commit()
        flash('Task deleted', 'success')
    except:
        db.session.rollback()
        flash('Could not delete task', 'error')
    
    # Check if project exists before redirecting (resilient to Vercel SQLite wipes)
    if Project.query.get(proj_id):
        return redirect(url_for('projects.view_project', project_id=proj_id))
    return redirect(url_for('projects.list_projects'))
