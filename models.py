from extensions import db
from flask_login import UserMixin
from datetime import datetime, date

# association table for project members (many-to-many)
project_members = db.Table('project_members',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('project_id', db.Integer, db.ForeignKey('project.id'))
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='member')  # 'admin' or 'member'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    
    # notification preferences
    notify_email = db.Column(db.Boolean, default=True)
    notify_tasks = db.Column(db.Boolean, default=True)
    
    # tasks assigned to this user
    assigned_tasks = db.relationship('Task', backref='assignee', lazy=True)
    
    def is_admin(self):
        return self.role == 'admin'
    
    def get_status(self):
        """return Active or Idle based on last activity"""
        if self.last_active:
            diff = datetime.utcnow() - self.last_active
            if diff.total_seconds() < 3600:  # active within 1 hour
                return 'Active'
        return 'Idle'
    
    def __repr__(self):
        return f'<User {self.username}>'

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # relationships
    tasks = db.relationship('Task', backref='project', lazy=True, cascade='all, delete-orphan')
    members = db.relationship('User', secondary=project_members, backref='projects')
    creator = db.relationship('User', foreign_keys=[created_by])
    
    def __repr__(self):
        return f'<Project {self.name}>'

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default='')
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed
    priority = db.Column(db.String(20), default='medium') # low, medium, high
    due_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # foreign keys
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    def is_overdue(self):
        """check if task is overdue"""
        if self.due_date and self.status != 'completed':
            return self.due_date < date.today()
        return False
    
    def status_display(self):
        # returns a nicer version of the status
        mapping = {
            'pending': 'Pending',
            'in_progress': 'In Progress',
            'completed': 'Completed'
        }
        return mapping.get(self.status, self.status)
    
    def __repr__(self):
        return f'<Task {self.title}>'
