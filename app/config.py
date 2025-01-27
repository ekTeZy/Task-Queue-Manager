import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default_secret_key') 
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')  
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "jwtsecretkey") 

    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0")