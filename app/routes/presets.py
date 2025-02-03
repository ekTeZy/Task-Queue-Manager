from flask import (
    Blueprint, 
    render_template, 
    redirect, 
    url_for,
    request,
    session,
    flash
)
from app.utils import validate_name
from app.models import Project
import json
from flask_jwt_extended import jwt_required, get_jwt_identity

presets_bp = Blueprint("dashboard_presets", __name__)

@presets_bp.route("/project_name", methods=["GET", "POST"])
@jwt_required()
def dashboard_step_1():
    user_id = int(get_jwt_identity())
    existing_project = Project.query.filter_by(user_id=user_id).first()
    
    if existing_project:
        return redirect(url_for("dashboard_main.dashboard_main", project=existing_project))

    if request.method == "POST":
        session["project_name"] = request.form.get("project_name", "Project").strip()
        
        if validate_name(session["project_name"]):
            return redirect(url_for("dashboard_presets.dashboard_step_2"))
        
        flash("Недопустимое название проекта.", "danger")
        return redirect(url_for("dashboard_presets.dashboard_step_1"))

    return render_template("dashboard_presets/step_1.html")



@presets_bp.route("/structure", methods=["GET", "POST"])
@jwt_required()
def dashboard_step_2():
    user_id = int(get_jwt_identity())
    existing_project = Project.query.filter_by(user_id=user_id).first()
    
    if existing_project:
        return redirect(url_for("dashboard_main.dashboard_main", project=existing_project))
    
    if request.method == "POST":
        selected_structure = request.form.get("selected_structure")
        session["project_structure"] = json.dumps(selected_structure if selected_structure else ["table_struct"])
        
        return redirect(url_for("dashboard_presets.dashboard_step_3"))

    return render_template("dashboard_presets/step_2.html")


@presets_bp.route("/task_fields", methods=["GET", "POST"])
@jwt_required()
def dashboard_step_3():
    user_id = int(get_jwt_identity())
    existing_project = Project.query.filter_by(user_id=user_id).first()
    
    if existing_project:
        return redirect(url_for("dashboard_main.dashboard_main", project=existing_project))    
    
    if request.method == "POST":
        selected_fields = [
            field for field in ["owner", "status", "due_date", "priority", "budget", "notes", "files", "last_updated"]
            if request.form.get(field)
        ]
        
        session["task_fields"] = json.dumps(selected_fields if selected_fields else ["status", "priority"])

        return redirect(url_for("dashboard_presets.dashboard_step_4"))

    return render_template("dashboard_presets/step_3.html")


@presets_bp.route("/task_groups", methods=["GET", "POST"])
@jwt_required()
def dashboard_step_4():
    user_id = int(get_jwt_identity())
    existing_project = Project.query.filter_by(user_id=user_id).first()
    
    if existing_project:
        return redirect(url_for("dashboard_main.dashboard_main", project=existing_project))    
    
    if request.method == "POST":
        selected_task_group = request.form.get("task_group")
        session["selected_task_group"] = json.dumps(selected_task_group if selected_task_group else json.loads(session.get("task_fields", '["status"]'))[0])

        return redirect(url_for("dashboard_main.dashboard_main"))
    
    return render_template("dashboard_presets/step_4.html")