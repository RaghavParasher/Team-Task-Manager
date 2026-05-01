from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import User
from extensions import db

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

@settings_bp.route('/')
@login_required
def settings_page():
    return render_template('settings.html')

@settings_bp.route('/update-profile', methods=['POST'])
@login_required
def update_profile():
    username = request.form.get('username', '').strip()
    email = request.form.get('email', '').strip()
    
    if not username or not email:
        flash('Name and email are required', 'error')
        return redirect(url_for('settings.settings_page'))
    
    # check if username taken by someone else
    existing = User.query.filter(User.username == username, User.id != current_user.id).first()
    if existing:
        flash('Username already taken', 'error')
        return redirect(url_for('settings.settings_page'))
    
    # check if email taken by someone else
    existing = User.query.filter(User.email == email, User.id != current_user.id).first()
    if existing:
        flash('Email already in use', 'error')
        return redirect(url_for('settings.settings_page'))
    
    current_user.username = username
    current_user.email = email
    db.session.commit()
    flash('Profile updated!', 'success')
    return redirect(url_for('settings.settings_page'))

@settings_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    old_password = request.form.get('old_password', '')
    new_password = request.form.get('new_password', '')
    confirm_password = request.form.get('confirm_password', '')
    
    if not old_password or not new_password:
        flash('Please fill in all password fields', 'error')
        return redirect(url_for('settings.settings_page'))
    
    if not check_password_hash(current_user.password_hash, old_password):
        flash('Current password is incorrect', 'error')
        return redirect(url_for('settings.settings_page'))
    
    if len(new_password) < 6:
        flash('New password must be at least 6 characters', 'error')
        return redirect(url_for('settings.settings_page'))
    
    if new_password != confirm_password:
        flash('New passwords do not match', 'error')
        return redirect(url_for('settings.settings_page'))
    
    current_user.password_hash = generate_password_hash(new_password)
    db.session.commit()
    flash('Password changed successfully!', 'success')
    return redirect(url_for('settings.settings_page'))

@settings_bp.route('/update-notifications', methods=['POST'])
@login_required
def update_notifications():
    current_user.notify_email = 'notify_email' in request.form
    current_user.notify_tasks = 'notify_tasks' in request.form
    db.session.commit()
    flash('Notification preferences saved!', 'success')
    return redirect(url_for('settings.settings_page'))
