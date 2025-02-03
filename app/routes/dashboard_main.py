from flask import (
    Blueprint, 
    render_template, 
    redirect, 
    url_for,
    request,
    session,
    flash
)
import json
from app.models import User, Project
from app import db
from flask_jwt_extended import jwt_required, get_jwt_identity

dashboard_bp = Blueprint("dashboard_main", __name__)

@dashboard_bp.route("/main", methods=["GET", "POST"])
@jwt_required()
def dashboard_main():

    user_id = int(get_jwt_identity())
    
    # вытаскиваем данные настроек проекта из сессии 
    project_name = session.get("project_name", "Project")
    project_structure = json.loads(session.get("project_structure", '["table_struct"]'))
    project_task_fields = json.loads(session.get("task_fields", '["status", "priority"]'))
    project_selected_task_group = json.loads(session.get("selected_task_group", json.dumps(project_task_fields[0])))        

    existing_project = Project.query.filter_by(user_id=user_id, name=project_name).first()
        
    if not existing_project:
        new_project = Project(
            name=project_name,
            structure=project_structure,
            key_fields=project_task_fields,
            task_groups=project_selected_task_group,
            user_id=user_id
        )

        try:
            db.session.add(new_project)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash("Failed to save project settings. Please try again.", "danger")
            return redirect(url_for("dashboard_presets.dashboard_step_1"))            

    project = existing_project if existing_project else new_project
    return render_template("dashboard_main/dashboard_main.html", project=project)


@dashboard_bp.route("/tasks", methods=["GET", "POST"])
@jwt_required()
def dashboard_tasks():
    return render_template("dashboard_main/dashboard_tasks.html")


@dashboard_bp.route("/settings", methods=["GET", "POST"])
@jwt_required()
def dashboard_settings():
    return render_template("dashboard_main/dashboard_settings.html")


@dashboard_bp.route("/analytics", methods=["GET", "POST"])
@jwt_required()
def dashboard_analytics():
    return render_template("dashboard_main/dashboard_analytics.html")