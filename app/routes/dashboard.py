from flask import (
    Blueprint, 
    render_template, 
    redirect, 
    url_for,
    request
)
from flask_jwt_extended import jwt_required

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/", methods=["GET", "POST"])
@jwt_required()
def dashboard_settings():
    if request.method == "GET":
        return render_template("dashboard_presets/dashboard.html")