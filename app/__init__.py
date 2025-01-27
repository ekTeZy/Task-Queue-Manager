from flask import Flask, render_template
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .routes import auth, index, dashboard
from dotenv import load_dotenv
# загрузка переменных окружения 
load_dotenv()

# инициализируем БД
db = SQLAlchemy()
from .models import User, Task, TaskLog, Goal
migrate = Migrate()


# создание приложения
def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="../static")
    
    app.config.from_object('app.config.Config')

    db.init_app(app)
    migrate.init_app(app, db)
    
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template('500.html'), 500
    
    app.register_blueprint(index.index_bp, url_prefix="/")
    app.register_blueprint(auth.auth_bp, url_prefix="/auth")
    app.register_blueprint(dashboard.dashboard_bp, url_prefix="/dashboard")
    

    return app