from app import db
from datetime import datetime, timedelta
from flask_jwt_extended import create_access_token, create_refresh_token
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    """Модель пользователя"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="user") 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    tasks = db.relationship('Task', backref='user', lazy=True)

    def get_token(self, access_expired_time=1, refresh_expired_time=7):
        """
        Генерирует access и refresh токены для пользователя.

        :param access_expired_time: Срок действия access токена (в часах).
        :param refresh_expired_time: Срок действия refresh токена (в днях).
        :return: Кортеж (access_token, refresh_token).
        """
        access_token = create_access_token(
            identity=str(self.id),
            additional_claims={"role": self.role},
            expires_delta=timedelta(hours=access_expired_time)
        )
        
        refresh_token = create_refresh_token(
            identity=str(self.id),  # Передаём только id как строку
            expires_delta=timedelta(days=refresh_expired_time)
        )
        
        return access_token, refresh_token

    def __init__(self, **kwargs):
        self.username = kwargs.get("username")
        self.email = kwargs.get("email")
        self.password = generate_password_hash(kwargs.get("password"))

    @classmethod
    def check_auth(cls, email, password):
        if not isinstance(email, str) or not isinstance(password, str):
            raise Exception("Invalid input: email and password must be strings")
        user = cls.query.filter(cls.email == email).one_or_none()

        if user is None:
            raise Exception("Invalid email")

        if not check_password_hash(user.password, password):
            raise Exception("Invalid password")

        return user
        
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
    
    
class Project(db.Model):
    """Модель проекта"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)  
    structure = db.Column(db.String(50), nullable=False, default="table_struct") 
    key_fields = db.Column(db.JSON, nullable=True)  
    task_groups = db.Column(db.JSON, nullable=True)  
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # связь с пользователем
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('projects', lazy=True))

    def __repr__(self):
        return f'<Project {self.name}>'


class TaskLog(db.Model):
    """Модель для логирования изменений задачи"""
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    action = db.Column(db.String(128))  # "status_updated", "priority_changed"
    old_value = db.Column(db.String(128), nullable=True)  # предыдущее значение
    new_value = db.Column(db.String(128), nullable=True)  # новое значение
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
