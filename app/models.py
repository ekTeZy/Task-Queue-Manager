from app import db
from datetime import datetime

class User(db.Model):
    """Модель пользователя"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default="user") 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    tasks = db.relationship('Task', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'


class Task(db.Model):
    """Модель задачи"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='new')  # new, in_progress, completed, canceled
    priority = db.Column(db.String(10), default='medium')  # low, medium, high
    deadline = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    goal_id = db.Column(db.Integer, db.ForeignKey('goal.id'), nullable=True)

    logs = db.relationship('TaskLog', backref='task', lazy=True)

    def __repr__(self):
        return f'<Task {self.title}>'


class TaskLog(db.Model):
    """Модель для логирования изменений задачи"""
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    action = db.Column(db.String(128))  # Например, "status_updated", "priority_changed"
    old_value = db.Column(db.String(128), nullable=True)  # Предыдущее значение
    new_value = db.Column(db.String(128), nullable=True)  # Новое значение
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<TaskLog {self.action} for Task {self.task_id}>'


class Goal(db.Model):
    """Модель целей пользователя"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=True)
    deadline = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tasks = db.relationship('Task', backref='goal', lazy=True)

    def __repr__(self):
        return f'<Goal {self.title}>'
