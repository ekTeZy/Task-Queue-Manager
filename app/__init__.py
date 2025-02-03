from flask import Flask, flash, render_template, redirect, url_for
import os
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
# загрузка переменных окружения 
load_dotenv()

# инициализируем БД
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()



# создание приложения
def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="../static")
    
    app.config.from_object('app.config.Config')

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    from .models import User, Task, TaskLog, Goal
    from .routes import auth, index, presets, dashboard_main
    
    @jwt.unauthorized_loader
    def unauthorized_callback(callback):
        flash("You must log in to access this page.", "warning")
        return redirect(url_for("auth.login"))
    
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template('500.html'), 500
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        flash("Your session has expired. Please log in again.", "warning")
        return redirect(url_for("auth.login"))
    
    app.register_blueprint(index.index_bp, url_prefix="/")
    app.register_blueprint(auth.auth_bp, url_prefix="/auth")
    app.register_blueprint(presets.presets_bp, url_prefix="/preset")
    app.register_blueprint(dashboard_main.dashboard_bp, url_prefix="/main")

    return app