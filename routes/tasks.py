from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from models import Task, Project, User
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
    
    return render_template('tasks.html', tasks=tasks)

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
        flash('You can only update your own tasks', 'error')
        return redirect(url_for('tasks.list_tasks'))
    
    new_status = request.form.get('status')
    
    if new_status not in ['pending', 'in_progress', 'completed']:
        flash('Invalid status', 'error')
        return redirect(url_for('tasks.list_tasks'))
    
    task.status = new_status
    db.session.commit()
    flash('Task status updated!', 'success')
    
    # redirect back to where they came from
    next_url = request.form.get('next', url_for('tasks.list_tasks'))
    return redirect(next_url)

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
    
    return redirect(url_for('projects.view_project', project_id=proj_id))
